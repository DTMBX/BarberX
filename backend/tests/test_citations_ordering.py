from backend.tools.law.citations import extract_citations


def test_citations_ordering():
    text = "In Smith v. Jones, 123 F.3d 456, and later in 234 U.S. 789 the court said..."
    cites = extract_citations(text)
    # deterministic: first match should be '123 F.3d 456', then '234 U.S. 789'
    assert len(cites) >= 2
    assert cites[0]["cite_text"] == "123 F.3d 456"
    assert cites[1]["cite_text"] == "234 U.S. 789"
