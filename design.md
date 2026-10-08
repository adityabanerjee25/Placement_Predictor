# PlacementPulse Design System

## Visual direction

PlacementPulse uses the attached Swapsmore references as the visual benchmark: warm editorial whitespace, expressive serif headlines, friendly blue calls to action, soft illustrated surfaces, and a dark contrast section near the bottom of the page.

The product adapts that same rhythm for a student-placement product. It should feel optimistic and human, never clinical or like a recruiting dashboard.

## Typography

- **Display:** Benne, with Georgia fallback. Use for hero headlines, section headlines, and card titles.
- **UI/body:** Manrope. Use for navigation, body copy, labels, buttons, and form controls.
- **Metadata:** JetBrains Mono. Use for small uppercase section kickers, step labels, model/version metadata, and technical status labels.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Benne&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&family=Manrope:wght@200..800&display=swap" rel="stylesheet">
```

## Color tokens

| Token | Value | Use |
|---|---|---|
| Cream | `#FFFAF3` | Page background and light cards |
| Ink | `#171C29` | Primary text and footer/dark surfaces |
| Placement blue | `#4775DA` | Primary CTA, links, progress states |
| Blue wash | `#EAF5F7` | Step labels and light support surfaces |
| Rule | `#E9E0D4` | Hairlines and FAQ separators |
| Success green | `#5EAA40` | Positive indicators |
| Warm orange | `#FAAC0B` | Accent doodles and attention states |
| Coral | `#F35A43` | Secondary accent and caution states |

## Layout rules

- Desktop content uses a centered max width of approximately 1180px.
- The page is intentionally generous: sections use large vertical spacing and short text blocks.
- Hero content is centered with decorative marks around the edges.
- Story sections alternate text and visual mock cards between left and right.
- Topic chips use rounded pill shapes and subtle shadows.
- Audience cards use a dark section with warm off-white cards.
- FAQ is narrow and quiet, with one row per question and a blue chevron.
- The final CTA is a rounded blue panel directly above the dark footer.

## Component patterns

### Primary button

Blue rounded pill, bold Manrope label, trailing arrow, and a soft blue shadow. Use for the main product action only.

### Step label

Small JetBrains Mono label in blue, optionally inside a pale-blue pill. Labels use uppercase copy such as `STEP 1`.

### Story card

White card, thin cool-blue border, 10-12px radius, and a soft shadow. Cards represent profile, readiness, focus, and progress rather than final product screens.

### Topic chip

White/cream pill with a one-color dot and Manrope label. Chips may be interactive later, but the landing page version is informational.

### Dark audience card

Warm white gradient on a dark ink section, 30px radius, editorial Benne title, and very light decorative line art or symbol in the lower corner.

## Future sections

Planned screens should preserve this system:

1. **Readiness intake:** Multi-step form using the same cream canvas, blue progress indicator, and short contextual copy.
2. **Resume review:** Upload surface with a large dashed boundary, extraction confidence chips, and explicit confirm/edit actions.
3. **Results:** Readiness score card, placement estimate, “what helped” and “what to work on” panels, plus the responsible-use disclaimer.
4. **Student dashboard:** Progress history, saved suggestions, profile completeness, and model version metadata.
5. **Coordinator view:** Cohort-level aggregates only, with privacy-safe summaries and no automatic student ranking.
6. **Model evaluation:** Internal vs external metrics, confusion matrix, dataset source, and evaluation date.

## Interaction rules

- Every primary CTA should lead to a clear next step.
- Accordions open inline and never navigate away.
- Form errors should appear beside the field in plain language.
- Extracted resume fields must be editable and confirmed before inference.
- Readiness and placement outputs must include a visible “estimate, not a guarantee” message.
- Never use color alone to communicate success, warning, or failure.

## Responsive behavior

- Navigation links collapse on small screens while the log-in action remains visible.
- Two-column story sections become stacked with the visual before the copy.
- Audience cards become one column.
- Topic chips wrap naturally and reduce padding.
- Decorative marks can be hidden on narrow screens if they compete with content.
