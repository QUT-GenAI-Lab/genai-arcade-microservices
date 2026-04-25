# Design System

## Overview

- Retro desktop interface inspired by Windows 95, rebuilt for the GenAI Arcade shell.
- High-contrast chrome, beveled borders, and icon-led navigation should make each page feel like a small desktop window rather than a flat marketing site.
- Content still needs modern readability: generous line-height, strong hierarchy, and clear card summaries for categories and games.

## Colors

- **Primary** (#00007f): active title bars, selected items, strongest interactive focus states
- **Secondary** (#bfb8bf): window chrome, frame surfaces, neutral shell backgrounds
- **Surface** (#fff8ff): content wells, explorer panes, cards, readable text areas
- **Surface Variant** (#cccccc): command buttons, status bars, raised controls
- **Accent** (#ad5d8d): page backdrop and nostalgic wallpaper tint
- **Outline Dark** (#000000): outer borders, pressed states, depth cues
- **Outline Light** (#fff8ff): highlight edges for raised controls and panels
- **Muted** (#7f787f): recessed frame edges and separator details
- **Text** (#111827): body copy and default labels
- **Link** (#0000ff): inline links and linked resources inside content windows

## Typography

- **Headline Font:** Tahoma, Geneva, Verdana, sans-serif
- **Body Font:** Tahoma, Geneva, Verdana, sans-serif
- **Label Font:** Tahoma, Geneva, Verdana, sans-serif
- Title bars use bold 14px text with tight spacing to mimic classic desktop chrome.
- Body copy stays around 14px with 1.6 line-height for readability inside dense windows.
- Small labels, status bars, and control text use 11-12px sizing with stronger weight instead of decorative typography.

## Elevation

Depth comes from beveled borders, inset wells, and pressed states rather than shadows. Raised elements use light top/left borders and dark bottom/right borders; inset regions reverse that logic to create the recessed explorer and content panels.

## Components

- **Window Frames:** 2px beveled chrome, blue title bars, 14px icon + label pairing, optional control buttons on the right.
- **Desktop Navigation Buttons:** Tall stacked icon/text buttons with raised surface styling; active press state inverts border treatment.
- **Explorer Tree:** File-explorer list with pixel guide lines, 16px icons, nested child pages, and blue active-row treatment.
- **Cards:** Recessed content cards with icon badge, eyebrow/meta line, bold title, and supporting summary copy.
- **Menu Bars:** Text-only horizontal command strip below the title bar with underlined accelerators when needed.
- **Status Bars:** Split readout fields using inset borders to echo classic footer chrome.
- **Pagers:** Three-column footer nav with home on left and previous/next actions centered.
- **Alerts / Notes:** Same window shell as content pages, but with warning icon and concise, centered messaging.

## Do's and Don'ts

- **Do** keep chrome colors and bevel logic consistent across every reusable shell component.
- **Do** use iconography to support hierarchy, especially in explorer trees, cards, and title bars.
- **Do** keep content surfaces bright and uncluttered so long-form educational copy stays readable.
- **Don't** replace beveled depth with modern drop shadows.
- **Don't** use more than one saturated accent color inside the same window.
- **Don't** hide important navigation behind hover-only affordances; links and buttons should remain obvious at rest.
