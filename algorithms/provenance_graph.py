"""
Algorithm B — Provenance Graph Builder
========================================
Builds a directed acyclic graph linking originals → derivatives → exports.

The graph captures the complete chain of transformations applied to evidence,
suitable for court package exports and the "Evidence Report" document.

Output formats:
  - JSON graph (nodes + edges) with SHA-256 integrity hash.
  - Summary statistics (total originals, derivatives, export artifacts).

Design constraints:
  - Read-only: never modifies evidence or manifests.
  - Deterministic: same evidence set → identical graph hash.
  - Tenant-isolated: only includes evidence within the authorized case.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from algorithms.base import AlgorithmBase, AlgorithmParams, hash_json
from algorithms.registry import registry

logger = logging.getLogger(__name__)


@registry.register
class ProvenanceGraphAlgorithm(AlgorithmBase):
    """Build a provenance graph linking originals, derivatives, and exports."""

    @property
    def algorithm_id(self) -> str:
        return "provenance_graph"

    @property
    def algorithm_version(self) -> str:
        return "1.0.0"

    def _execute(
        self, params: AlgorithmParams, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build the provenance graph for a case.

        Context keys:
          - db_session: SQLAlchemy session.
          - evidence_store: EvidenceStore instance.

        Returns payload with:
          - nodes: List of node dicts (hash, type, metadata).
          - edges: List of edge dicts (source_hash, target_hash, transformation).
          - statistics: Summary counts.
          - graph_hash: SHA-256 of the canonical graph.
        """
        db_session = context["db_session"]
        evidence_store = context["evidence_store"]

        from models.evidence import EvidenceItem, CaseEvidence, ChainOfCustody
        from models.legal_case import LegalCase

        # Tenant isolation
        case = db_session.query(LegalCase).filter_by(
            id=params.case_id, organization_id=params.tenant_id
        ).first()
        if not case:
            raise ValueError(f"Case {params.case_id} not found or access denied")

        # Get evidence linked to this case
        links = (
            db_session.query(CaseEvidence)
            .filter_by(case_id=params.case_id)
            .filter(CaseEvidence.unlinked_at.is_(None))
            .all()
        )
        evidence_ids = [link.evidence_id for link in links]

        items = (
            db_session.query(EvidenceItem)
            .filter(EvidenceItem.id.in_(evidence_ids))
            .all()
        ) if evidence_ids else []

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        input_hashes: List[str] = []

        for item in items:
            if not item.hash_sha256:
                continue

            input_hashes.append(item.hash_sha256)

            # Node for the original
            nodes.append({
                "hash": item.hash_sha256,
                "type": "original",
                "evidence_id": item.id,
                "evidence_store_id": item.evidence_store_id,
                "original_filename": item.original_filename,
                "file_type": item.file_type,
                "file_size_bytes": item.file_size_bytes,
                "collected_date": (
                    item.collected_date.isoformat()
                    if item.collected_date
                    else None
                ),
            })

            # Load manifest for derivatives
            if item.evidence_store_id:
                manifest = evidence_store.load_manifest(item.evidence_store_id)
                if manifest and hasattr(manifest, "derivatives"):
                    for deriv in manifest.derivatives:
                        nodes.append({
                            "hash": deriv.sha256,
                            "type": "derivative",
                            "derivative_type": deriv.derivative_type,
                            "filename": deriv.filename,
                            "size_bytes": deriv.size_bytes,
                            "created_at": deriv.created_at,
                            "parameters": deriv.parameters,
                        })
                        edges.append({
                            "source_hash": item.hash_sha256,
                            "target_hash": deriv.sha256,
                            "transformation": deriv.derivative_type,
                            "parameters": deriv.parameters,
                        })

            # Chain of custody entries (for export edges)
            custody_entries = (
                db_session.query(ChainOfCustody)
                .filter_by(evidence_id=item.id)
                .filter(ChainOfCustody.action.like("%export%"))
                .order_by(ChainOfCustody.action_timestamp)
                .all()
            )
            for entry in custody_entries:
                if entry.hash_after and entry.hash_after != item.hash_sha256:
                    nodes.append({
                        "hash": entry.hash_after,
                        "type": "export",
                        "action": entry.action,
                        "timestamp": (
                            entry.action_timestamp.isoformat()
                            if entry.action_timestamp
                            else None
                        ),
                        "actor": entry.actor_name,
                    })
                    edges.append({
                        "source_hash": item.hash_sha256,
                        "target_hash": entry.hash_after,
                        "transformation": entry.action,
                    })

        # Deduplicate nodes by hash
        seen_hashes = set()
        unique_nodes = []
        for node in nodes:
            if node["hash"] not in seen_hashes:
                seen_hashes.add(node["hash"])
                unique_nodes.append(node)

        # Sort for determinism
        unique_nodes.sort(key=lambda n: n["hash"])
        edges.sort(key=lambda e: (e["source_hash"], e["target_hash"]))

        # Statistics
        type_counts = defaultdict(int)
        for node in unique_nodes:
            type_counts[node["type"]] += 1

        graph = {
            "case_id": params.case_id,
            "nodes": unique_nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(unique_nodes),
                "total_edges": len(edges),
                "originals": type_counts.get("original", 0),
                "derivatives": type_counts.get("derivative", 0),
                "exports": type_counts.get("export", 0),
            },
        }
        graph_hash = hash_json(graph)
        graph["graph_hash"] = graph_hash

        return {
            **graph,
            "output_hashes": [graph_hash],
            "input_hashes": input_hashes,
        }
