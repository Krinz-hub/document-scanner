# UI Design System

## Visual direction
Professional verification workstation. Minimal, quiet, information-first.

## Avoid
- Cards around every section
- Thick borders
- Excessive rounded rectangles
- Giant gradients
- Glassmorphism
- Decorative AI graphics
- Huge status cards
- Excessive shadows
- Meaningless metrics

## Use
- Whitespace
- Typography hierarchy
- Subtle 1px dividers between sections
- Small status dots
- Compact tables/data rows
- Strong alignment
- Clear evidence hierarchy
- One primary action at a time

## Main screen

```text
SCREENING
Passport
Review required

────────────────────────────

IDENTITY
Name                 ...
Nationality           ...
Date of birth        ...

DOCUMENT
Passport number      ...
Expiry               Valid
MRZ                  Valid

VERIFICATION
External status      Valid
Face comparison      Match

ANALYSIS
Photo                Review
Text                 No anomaly
Stamp                Insufficient evidence

────────────────────────────

REASONS FOR REVIEW
• DOB inconsistency
• Possible photo manipulation

[View evidence]    [Manual review]
```

## Global CSS tokens

```css
:root {
  --bg: #f7f7f5;
  --surface: #ffffff;
  --text: #171717;
  --muted: #6b6b67;
  --line: #e7e7e2;

  --success: #287a55;
  --warning: #9a6a16;
  --danger: #b23a32;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;

  --radius-sm: 6px;
  --content-width: 1280px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.page {
  width: min(100% - 32px, var(--content-width));
  margin-inline: auto;
  padding-block: var(--space-7);
}

.section {
  padding-block: var(--space-5);
}

.section + .section {
  border-top: 1px solid var(--line);
}

.data-row {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 24px;
  padding-block: 12px;
  border-bottom: 1px solid var(--line);
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-weight: 600;
}

.status::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

@media (max-width: 800px) {
  .page {
    width: min(100% - 24px, var(--content-width));
  }

  .data-row {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
```
