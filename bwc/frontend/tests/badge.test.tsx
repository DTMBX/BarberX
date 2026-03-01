import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/badge';

describe('Badge component', () => {
  it('renders text content', () => {
    render(<Badge>Verified</Badge>);
    expect(screen.getByText('Verified')).toBeInTheDocument();
  });

  it('applies variant class for verified', () => {
    const { container } = render(<Badge variant="verified">OK</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('emerald');
  });

  it('applies variant class for error', () => {
    const { container } = render(<Badge variant="error">Fail</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('red');
  });

  it('applies variant class for pending', () => {
    const { container } = render(<Badge variant="pending">Wait</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('yellow');
  });

  it('defaults to neutral variant', () => {
    const { container } = render(<Badge>Default</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('slate');
  });

  it('passes custom className', () => {
    const { container } = render(<Badge className="custom-test">X</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('custom-test');
  });
});
