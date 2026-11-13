---
name: Clinical Clarity
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#3e4943'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#6e7a72'
  outline-variant: '#bdcac1'
  surface-tint: '#006c4c'
  primary: '#00694a'
  on-primary: '#ffffff'
  primary-container: '#07855e'
  on-primary-container: '#f5fff7'
  inverse-primary: '#74daad'
  secondary: '#556158'
  on-secondary: '#ffffff'
  secondary-container: '#d9e6da'
  on-secondary-container: '#5b675e'
  tertiary: '#5a5c5c'
  on-tertiary: '#ffffff'
  tertiary-container: '#737575'
  on-tertiary-container: '#fcfcfc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#90f6c8'
  primary-fixed-dim: '#74daad'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#005138'
  secondary-fixed: '#d9e6da'
  secondary-fixed-dim: '#bdcabe'
  on-secondary-fixed: '#131e17'
  on-secondary-fixed-variant: '#3e4a41'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c7'
  on-tertiary-fixed: '#1a1c1c'
  on-tertiary-fixed-variant: '#454747'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-sm:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  label-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.2'
  caption:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 120px
  max-width-content: 1200px
---

## Brand & Style
The design system is engineered for "MedicineCabinet," a healthcare utility where trust, clarity, and accessibility are paramount. The brand personality is clinical yet compassionate—balancing the precision of a medical instrument with the approachability of a local pharmacy.

The aesthetic follows a **Modern Minimalist** movement with **Tactile/Card-based** influences. It prioritizes high legibility and intentional whitespace to reduce cognitive load for users who may be managing complex health data or medications. The interface evokes a sense of organized calm through structured layouts and a restrained color palette.

## Colors
The palette is centered on "Healing Green" to symbolize health and safety. 
- **Primary Green (#2D9971):** Used for primary actions, branding, and status indicators. It meets WCAG AA standards for contrast against white backgrounds.
- **Secondary Soft Green (#E8F5E9):** Employed for large surface areas, background tints, and card containers to provide a gentle visual rest.
- **Pure White (#FFFFFF):** The primary surface color for cards and input fields to maintain a "sterile" and clean environment.
- **Dark Charcoal (#1A1A1A):** Reserved strictly for typography and iconography to ensure maximum readability and accessibility.
- **Success/Warning/Error:** Utilize the Primary Green for success; use a muted amber for warnings and a soft crimson for errors, always maintaining the 18px minimum text size within these states.

## Typography
This design system utilizes **Inter** for its exceptional legibility and systematic structure. 
- **Size Floor:** The absolute minimum font size for body content is 18px to accommodate users with varying visual abilities.
- **Hierarchy:** Large headings use a tighter letter spacing and heavy weights to create clear section anchoring. 
- **Readability:** Line heights are set generously (1.6x for body) to prevent "crowding" of medical information, which is critical when reading dosage instructions or drug names.

## Layout & Spacing
The design system employs a **Fluid Grid** with fixed maximum constraints for readability.
- **Mobile First:** Layouts stack vertically with a 16px side margin. Touch targets are a minimum of 48x48px.
- **Desktop Optimization:** Content is centered within a 1200px max-width container. 
- **Rhythm:** An 8px base unit drives all spacing. For healthcare clarity, "Generous" is the default—use `md` (24px) for internal card padding and `lg` (48px) for section vertical spacing.
- **Reflow:** On tablet/desktop, medication lists transition from single-column stacks to a multi-column grid (up to 3 columns) to reduce vertical scrolling.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** combined with **Ambient Shadows**. 
- **Surface 0:** The global background uses the Secondary Soft Green (#E8F5E9).
- **Surface 1 (Cards):** Pure White (#FFFFFF) cards sit on the background.
- **Shadows:** Use a "Clinical Shadow"—very soft, highly diffused, with a slight green tint to maintain harmony. 
  - *Example:* `0px 4px 20px rgba(45, 153, 113, 0.08)`.
- **Interactive States:** On hover or focus, the shadow depth increases slightly, and the card may lift (translate -2px) to provide tactile feedback for touch and mouse users.

## Shapes
The shape language is defined by a consistent 16px (1rem) corner radius. This "Rounded" approach softens the clinical nature of the tool, making it feel more friendly and modern.
- **Cards & Modals:** Use the `rounded-lg` (1rem/16px) standard.
- **Buttons:** Follow the same 16px radius.
- **Inputs:** Utilize a slightly smaller radius (8px) for a more structured feel within the larger card containers.
- **Avatars/Icons:** Use circular (pill) shapes for profile images or status pips.

## Components
- **Buttons:** Large format (56px height for primary). Solid #2D9971 background with White text. Secondary buttons use a thick 2px border in Primary Green.
- **Cards:** The primary container for medication info. White background, 16px radius, subtle shadow, and 24px internal padding.
- **Input Fields:** 18px text, 56px height. Borders use a soft grey that shifts to Primary Green on focus. Labels sit permanently above the field (no floating labels) for persistent context.
- **Chips/Tags:** Used for medication categories (e.g., "Prescription," "Vitamin"). Light tint of the category color with 16px text.
- **Lists:** High-contrast rows with 16px vertical spacing between items. Each list item should have a clear "Action" area (Chevron or Toggle).
- **Dosage Toggle:** Custom radio buttons that look like large tiles for easy selection between "Morning," "Noon," "Evening," and "Night."