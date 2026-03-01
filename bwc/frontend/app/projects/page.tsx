'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listProjects, createProject, type Project } from '@/lib/api';
import {
  useToast,
  Button,
  Input,
  Textarea,
  PageHeader,
  Card,
  CardContent,
  EmptyState,
} from '@/components/ui';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      const data = await listProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createProject(name, 'default-user', description || undefined);
      addToast('success', 'Project created');
      setName('');
      setDescription('');
      setShowForm(false);
      await loadProjects();
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Projects"
        actions={
          <Button
            onClick={() => setShowForm(!showForm)}
            variant={showForm ? 'secondary' : 'primary'}
            data-testid="projects-new-btn"
          >
            {showForm ? 'Cancel' : 'New Project'}
          </Button>
        }
      />

      {showForm && (
        <Card className="mt-6">
          <CardContent>
            <form onSubmit={handleCreate} className="space-y-4" data-testid="projects-form">
              <Input
                label="Project Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="e.g., Johnson v. City PD"
                data-testid="projects-name-input"
              />
              <Textarea
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                placeholder="Optional description..."
                data-testid="projects-description-input"
              />
              <Button
                type="submit"
                loading={submitting}
                disabled={!name}
                data-testid="projects-submit-btn"
              >
                Create Project
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="mt-6">
        {loading && <p className="text-slate-400 text-sm">Loading projects...</p>}
        {error && (
          <div className="rounded-lg border border-red-600/30 bg-red-900/20 p-4">
            <p className="text-sm text-red-300">Error: {error}</p>
          </div>
        )}

        {!loading && !error && projects.length === 0 && (
          <Card>
            <EmptyState
              title="No projects yet"
              description="Projects group related cases together"
              action={
                <Button
                  size="sm"
                  onClick={() => setShowForm(true)}
                  data-testid="projects-empty-create-btn"
                >
                  Create your first project
                </Button>
              }
            />
          </Card>
        )}

        {projects.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <Link key={p.id} href={`/cases?project_id=${p.id}`}>
                <Card className="hover:bg-slate-700/50 transition-colors h-full">
                  <CardContent>
                    <h3 className="font-semibold text-blue-400 text-lg">{p.name}</h3>
                    {p.description && (
                      <p className="text-slate-400 text-sm mt-1">{p.description}</p>
                    )}
                    <p className="text-slate-500 text-xs mt-3">
                      Created {new Date(p.created_at).toLocaleDateString()}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
