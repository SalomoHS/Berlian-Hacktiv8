# Car AI Chat - Design Specification

## Concept & Vision

A warm, inviting AI car recommendation assistant that feels like chatting with a knowledgeable friend at a premium showroom. The interface combines the precision of automotive engineering with the approachability of modern conversational design—clean lines, confident typography, and subtle motion that guides without overwhelming.

**Personality**: Friendly expert, not a chatbot. Confident but never pushy. Indonesian language first.

## Design Language

### Aesthetic Direction
**"Premium Showroom Meets Digital Companion"** — Inspired by luxury automotive brand websites (Mercedes, BMW configurators) combined with the warmth of Indonesian hospitality. Clean, spacious layouts with confident use of color and typography.

### Color Palette
- **Primary**: `#0891B2` (Cyan 600) — Trust, technology, modern
- **Primary Light**: `#22D3EE` (Cyan 400) — Hover states, accents
- **Secondary**: `#0D9488` (Teal 600) — Success states, secondary actions
- **Accent**: `#F97316` (Orange 500) — Highlights, CTAs, energy
- **Background**: `#FAFBFC` (Near white with slight warmth)
- **Surface**: `#FFFFFF` (Pure white cards)
- **Text Primary**: `#1E293B` (Slate 800)
- **Text Secondary**: `#64748B` (Slate 500)
- **Text Muted**: `#94A3B8` (Slate 400)
- **Border**: `#E2E8F0` (Slate 200)

### Typography
- **Display**: "Plus Jakarta Sans" (Google Fonts) — Bold, geometric, modern
- **Body**: "Inter" — Clean, highly readable at all sizes
- **Fallback**: system-ui, -apple-system, sans-serif

### Spatial System
- Base unit: 4px
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96
- Border radius: 8px (small), 12px (medium), 16px (large), 9999px (pill)
- Max chat width: 768px (optimal reading width)
- Mobile breakpoint: 640px

### Motion Philosophy
- **Purposeful**: Every animation serves navigation or feedback
- **Subtle**: 200-300ms for micro-interactions, 400ms for entrances
- **Physics-based**: Ease-out curves for natural feel
- Key animations:
  - Message entrance: Fade up + slide (200ms)
  - Typing indicator: Gentle bounce loop
  - Button hover: Scale 1.02 + shadow lift
  - Card hover: Subtle shadow expansion

### Visual Assets
- **Icons**: Lucide React (consistent stroke width, rounded)
- **Decorative**: Subtle gradient meshes, soft shadows, glassmorphism on header
- **Illustrations**: Abstract car silhouettes in brand colors for empty states

## Layout & Structure

### Page Architecture
```
┌─────────────────────────────────────────┐
│  Header (glassmorphism, sticky)         │
│  Logo + Nav (desktop) / Hamburger (mob) │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Chat Container (centered)      │   │
│  │  ┌───────────────────────────┐  │   │
│  │  │  Welcome Card (when empty) │  │   │
│  │  └───────────────────────────┘  │   │
│  │  ┌───────────────────────────┐  │   │
│  │  │  Message Bubbles          │  │   │
│  │  │  (AI left, User right)    │  │   │
│  │  └───────────────────────────┘  │   │
│  │  ┌───────────────────────────┐  │   │
│  │  │  Input Area (fixed bottom│  │   │
│  │  └───────────────────────────┘  │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Responsive Strategy
- **Desktop (>1024px)**: Full layout, generous whitespace
- **Tablet (768-1024px)**: Condensed spacing, same layout
- **Mobile (<768px)**: Full-width chat, bottom-anchored input, hamburger nav

## Features & Interactions

### Core Features

1. **Chat Interface**
   - Real-time streaming responses (character-by-character)
   - Message history persists during session
   - Loading states with animated indicators
   - Markdown rendering for AI responses

2. **Welcome Experience**
   - Animated greeting with typing effect
   - Quick action buttons (suggested questions)
   - Car brand icons for visual interest

3. **Input Area**
   - Auto-expanding textarea (max 4 lines)
   - Send button with loading state
   - Character hints for long messages
   - Keyboard shortcuts (Enter to send, Shift+Enter for newline)

4. **Message Bubbles**
   - User: Right-aligned, primary color background
   - AI: Left-aligned, white background with subtle shadow
   - Timestamps on hover (desktop)
   - Copy button on hover

### Interaction Details

| Element | Hover | Active | Loading |
|---------|-------|--------|---------|
| Send Button | Scale 1.02, shadow lift | Scale 0.98 | Spinner icon, disabled |
| Message | Subtle shadow | — | Typing dots animation |
| Quick Action | Background fill | Scale 0.98 | — |
| Nav Link | Underline slide | Bold weight | — |

### Error Handling
- Network error: Toast notification + retry button
- Empty input: Gentle shake animation on input
- Long response: Progressive loading messages

## Component Inventory

### 1. Header
- Glassmorphism background (`backdrop-blur-md`, 80% opacity white)
- Logo with subtle gradient
- Navigation links with underline hover animation
- Mobile: Hamburger menu with slide-out drawer

### 2. ChatContainer
- Max-width 768px, centered
- Padding: 24px (desktop), 16px (mobile)
- Min-height: calc(100vh - header)

### 3. WelcomeCard
- Animated entrance (fade + slide up)
- Large greeting text with brand accent
- 3 quick action buttons in grid
- Decorative car icon/illustration

### 4. MessageBubble
- **User variant**: Cyan background, white text, right-aligned, rounded-l-lg rounded-tr-lg
- **AI variant**: White background, slate text, left-aligned, rounded-r-lg rounded-tl-lg
- Shadow: `shadow-sm` (AI), none (user)
- Padding: 16px
- Max-width: 85% of container

### 5. TypingIndicator
- Three dots with staggered bounce animation
- Container matches AI bubble style
- Text: "Tony sedang mengetik..."

### 6. InputArea
- Sticky bottom position (mobile: fixed)
- White background with top border
- Input: Rounded-full, shadow-sm, focus ring
- Send button: Icon-only, circular, accent color

### 7. QuickActionButton
- Pill shape, border style
- Icon + text
- Hover: Fill with primary light
- Click: Ripple effect

## Technical Approach

### Stack
- React 18 with Vite
- Tailwind CSS for styling
- Lucide React for icons
- react-markdown + remark-gfm for markdown

### Key Implementation Details
- CSS custom properties for theme tokens
- useRef for scroll-to-bottom behavior
- localStorage for session persistence (optional)
- CSS animations (no external animation library needed)

### Performance Considerations
- Lazy load markdown parser
- Virtual scrolling for long conversations (future)
- Debounced input for typing indicator
