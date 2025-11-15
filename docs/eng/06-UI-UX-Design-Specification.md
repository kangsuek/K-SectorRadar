## 1. Design Principles

### 1.1 Basic Principles
- **Clarity**: Intuitive and clear information delivery centered on data
- **Consistency**: Use consistent design language across all pages
- **Accessibility**: Accessible in various user environments
- **Responsiveness**: Fast feedback and smooth interactions
- **Mobile First**: Responsive design prioritizing mobile environment

### 1.2 Design Concept
- Modern and minimal design
- Data-centered information delivery
- Intuitive navigation
- Efficient information hierarchy

---

## 2. Design System

### 2.1 Color Palette

#### 2.1.1 Primary Colors

| Color | HEX Code | Usage |
|------|----------|-------|
| **Primary Color** | #2563EB (Blue) | Primary user interaction elements, links, main buttons |
| **Secondary Color** | #10B981 (Green) | Secondary actions, success states |
| **Background** | #FFFFFF (White) | Page background |
| **Surface** | #F9FAFB (Light Gray) | Card, panel background |
| **Text Primary** | #111827 (Dark Gray) | Primary text |
| **Text Secondary** | #6B7280 (Medium Gray) | Secondary text |

#### 2.1.2 Status Colors

| Status | HEX Code | Usage |
|--------|----------|-------|
| **Success** | #10B981 (Green) | Success messages, completed states |
| **Error** | #EF4444 (Red) | Error messages, warning states |
| **Warning** | #F59E0B (Orange) | Warning messages |
| **Info** | #3B82F6 (Blue) | Information messages |

#### 2.1.3 Stock-Related Colors

| Status | HEX Code | Usage |
|--------|----------|-------|
| **Rise** | #EF4444 (Red) | Used when stock/change rate rises |
| **Fall** | #3B82F6 (Blue) | Used when stock/change rate falls |
| **Unchanged** | #6B7280 (Gray) | No change |

#### 2.1.4 Dark Mode Colors

| Color | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| **Background** | #FFFFFF | #111827 | Page background |
| **Surface** | #F9FAFB | #1F2937 | Card, panel background |
| **Text Primary** | #111827 | #F9FAFB | Primary text |
| **Text Secondary** | #6B7280 | #9CA3AF | Secondary text |
| **Border** | #E5E7EB | #374151 | Borders, dividers |
| **Primary Color** | #2563EB | #3B82F6 | Primary user interaction elements (slightly brighter in dark mode) |
| **Secondary Color** | #10B981 | #10B981 | Secondary actions (same in both modes) |
| **Rise** | #EF4444 | #F87171 | Stock/change rate rises (slightly brighter in dark mode) |
| **Fall** | #3B82F6 | #60A5FA | Stock/change rate falls (slightly brighter in dark mode) |

### 2.2 Typography

#### 2.2.1 Fonts
- **Headings**: System font (Bold, 24px~32px)
- **Body**: System font (Regular, 14px~16px)
- **Small Text**: System font (Regular, 12px)

#### 2.2.2 Font Size System

| Element | Size | Usage |
|---------|------|-------|
| **H1** | 32px | Page title |
| **H2** | 24px | Section title, stock card current price |
| **H3** | 20px | Subtitle |
| **Body** | 16px | Body text |
| **Small** | 14px | Secondary text, stock card bottom information |
| **Caption** | 12px | Caption, badge text |

### 2.3 Spacing System
- **Base Unit**: 4px grid system
- **Base Spacing**: 8px, 16px, 24px, 32px, 48px
- All padding and margins use multiples of 4px

### 2.4 Shadows

#### 2.4.1 Light Mode Shadows

| Shadow Type | Value | Usage |
|-------------|-------|-------|
| **Card Shadow** | 0 1px 3px rgba(0,0,0,0.1) | Default card shadow |
| **Hover Shadow** | 0 4px 6px rgba(0,0,0,0.1) | Card shadow on hover |
| **Elevated Shadow** | 0 10px 15px rgba(0,0,0,0.1) | Higher level element shadow |

#### 2.4.2 Dark Mode Shadows

| Shadow Type | Value | Usage |
|-------------|-------|-------|
| **Card Shadow** | 0 1px 3px rgba(0,0,0,0.3) | Default card shadow (stronger in dark mode) |
| **Hover Shadow** | 0 4px 6px rgba(0,0,0,0.4) | Card shadow on hover (stronger in dark mode) |
| **Elevated Shadow** | 0 10px 15px rgba(0,0,0,0.5) | Higher level element shadow (stronger in dark mode) |

### 2.5 Dark Mode Support

#### 2.5.1 Theme Toggle
- **Location**: Header (right side, next to GitHub link)
- **Icon**: Sun/Moon icon (Material Icons or Heroicons)
- **Interaction**: Click to toggle between light and dark mode
- **Persistence**: User preference saved in localStorage
- **Default**: Follows system preference (prefers-color-scheme media query)

#### 2.5.2 Transition
- **Duration**: 300ms smooth transition when switching themes
- **Scope**: All color properties transition smoothly
- **Performance**: Use CSS custom properties (CSS variables) for efficient theme switching

#### 2.5.3 Color Contrast
- **WCAG AA Compliance**: Maintain 4.5:1 contrast ratio in both light and dark modes
- **Text Readability**: Ensure all text remains readable in both themes
- **Stock Colors**: Rise/Fall colors adjusted for better visibility in dark mode

---

## 3. Common Components

### 3.1 Header

#### 3.1.1 Components
- Logo and site name (left)
- Navigation menu (center)
  - Dashboard
  - Comparison
  - Settings
- Theme toggle button (right, before GitHub link)
- GitHub link (right)

#### 3.1.2 Style

| Property | Light Mode | Dark Mode |
|----------|------------|-----------|
| Height | 64px | 64px |
| Background Color | #FFFFFF | #111827 |
| Bottom Border | 1px solid #E5E7EB | 1px solid #374151 |
| Position | Sticky (fixed) | Sticky (fixed) |

#### 3.1.3 Interaction
- Logo click navigates to home (Dashboard)
- Theme toggle button click switches between light and dark mode
- Theme preference persists across page reloads

### 3.2 Button

#### 3.2.1 Button Types
- **Primary**: Primary action (background color: Primary Color)
- **Secondary**: Secondary action (background color: Secondary Color)
- **Text**: Text button (no background)

#### 3.2.2 Style

| Property | Value |
|----------|-------|
| Height | 40px |
| Padding | 12px 24px |
| Border Radius | 8px |
| Hover Effect | Background color change |

### 3.3 Card

#### 3.3.1 Style

| Property | Light Mode | Dark Mode |
|----------|------------|-----------|
| Background Color | #FFFFFF | #1F2937 |
| Border Radius | 12px | 12px |
| Shadow | Card Shadow | Card Shadow (dark mode) |
| Padding | 24px | 24px |
| Hover Effect | Changes to Hover Shadow | Changes to Hover Shadow (dark mode) |

### 3.4 Badge

#### 3.4.1 Types

| Type | Background Color | Usage |
|------|------------------|-------|
| **STOCK** | #2563EB (Blue) | Stock display |
| **ETF** | #10B981 (Green) | ETF display |

#### 3.4.2 Style

| Property | Value |
|----------|-------|
| Height | 24px |
| Padding | 4px 12px |
| Border Radius | 12px |
| Font Size | 12px |

---

## 4. Page-by-Page UI Design

### 4.1 Dashboard Page

#### 4.1.1 Layout Structure
```
┌─────────────────────────────────────────┐
│              Header                     │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  Title and Stock Count            │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Filter/Sort + Update Info       │  │
│  └──────────────────────────────────┘  │
│  ┌──────┐  ┌──────┐  ┌──────┐        │
│  │ Card │  │ Card │  │ Card │        │
│  └──────┘  └──────┘  └──────┘        │
│  ┌──────┐  ┌──────┐                  │
│  │ Card │  │ Card │                  │
│  └──────┘  └──────┘                  │
└─────────────────────────────────────────┘
```

#### 4.1.2 Header Area
- **Title**: "SectorRadar Dashboard" (H1, 32px)
- **Stock Count**: "Total 6 stocks" (Body, 16px, Text Secondary)

#### 4.1.3 Filter and Update Area Details

| Item | Position/UI | Detailed Requirements |
|------|-------------|----------------------|
| **Sort Options** | Right-aligned, dropdown UI | Provides by type (default), by name, by theme, by change rate, by volume |
| **Update Time** | Center-aligned text | Displays final update time in "HH:MM:SS" format |
| **Auto Refresh Toggle** | Center-aligned, checkbox | Provides On/Off functionality with "Auto Refresh (30 seconds)" text |
| **Refresh Button** | Right-aligned | Button to manually refresh all data |

#### 4.1.4 Stock Card (StockCard) Detailed Design

| Area | Display Information | Style Features |
|------|---------------------|----------------|
| **Header** | Stock name, type badge, theme information | Clear text/badge distinction |
| **Price** | Current price, change rate, open/high/low price, volume, weekly change rate | Current price is **H2** (24px) size, change rate applies status color |
| **Mini Chart** | 6 days of price movement (candlestick) | Positioned at card center, compact size |
| **Trading Trends** | Individual/institutional/foreign trading volume (net buy/net sell) | Displays amount and sign together, **red/blue** color distinction for net buy/net sell |
| **Other** | Latest news headline 1, news count, stock code, fee (ETF only) | Placed at bottom, font size Small (14px) |

**Card Layout**
```
┌─────────────────────────────────────┐
│ [Stock Name] [Type Badge]            │
│ Theme: Nuclear/Power Plant/Energy   │
├─────────────────────────────────────┤
│  Current Price: 83,100              │
│  Change Rate: +2.5% (Red)           │
│  Open | High | Low                  │
│  82,000 | 83,500 | 81,800           │
│  Volume: 7.9M                       │
│  Weekly Change Rate: +5.2%          │
├─────────────────────────────────────┤
│  [Mini Chart Area]                  │
├─────────────────────────────────────┤
│  Trading Trends (2025-11-13)        │
│  Individual: -860K (Blue)           │
│  Institution: +220K (Red)           │
│  Foreign: +650K (Red)                │
├─────────────────────────────────────┤
│  Latest News: 11 articles            │
│  [Latest News Headline]              │
│  Stock Code: 034020                  │
│  Fee: 0.0045% (ETF only)            │
└─────────────────────────────────────┘
```

**Card Style**

| Property | Value |
|----------|-------|
| Width | Responsive (Mobile: 100%, Tablet: 50%, Desktop: 33.33%) |
| Minimum Height | 400px |
| Grid Gap | 24px |

### 4.2 Detail Page

#### 4.2.1 Layout Structure
- **Top**: Stock basic information (stock name, type, theme, current price, change rate, etc.)
- **Middle**: Detailed charts and statistics (price chart, volume chart, technical indicators)
- **Bottom**: News list and detailed trading trends (full news list, detailed trading trends)

### 4.3 Comparison Page

#### 4.3.1 Layout Structure
- **Left**: Stock selection area (checkboxes or dropdown)
- **Right**: Comparison result display area (comparison table, charts)

### 4.4 Settings Page

#### 4.4.1 Layout Structure
- Settings organized by section
- Each setting item displayed as a card
- Includes toggles, input fields, selection options, etc.

#### 4.4.2 Theme Settings
- **Theme Selection**: Toggle between Light, Dark, and System (follows OS preference)
- **Location**: Top of settings page, in "Appearance" section
- **Options**:
  - Light Mode
  - Dark Mode
  - System (Auto)
- **Visual Feedback**: Preview of selected theme

---

## 5. Interaction Design

### 5.1 Hover Effects
- **Card**: Shadow increase (Card Shadow → Hover Shadow)
- **Button**: Background color change
- **Link**: Underline display

### 5.2 Click Effects
- **Button**: Press effect (Active State, Scale effect)
- **Card**: Click navigates to detail page

### 5.3 Loading States
- **Spinner**: Displayed during data loading
- **Skeleton UI**: Optional use (during initial loading)

### 5.4 Error States
- **Error Message**: Clear error message display
- **Retry Button**: Provides retry functionality

---

## 6. Responsive Design (Mobile First)

### 6.1 Breakpoints

| Device | Screen Width | Stock Card Layout |
|--------|--------------|-------------------|
| **Mobile** | 0px ~ 768px | **1 column layout** |
| **Tablet** | 768px ~ 1024px | **2 column layout** |
| **Desktop** | 1024px and above | **3 column layout**, max width 1400px center-aligned |

### 6.2 Mobile Support
- Cards: 1 column layout
- Header: Hamburger menu (optional)
- Font size adjustment
- Touch-friendly button size (minimum 44px)

### 6.3 Tablet Support
- Cards: 2 column layout
- Spacing adjustment
- Maintain medium font size

### 6.4 Desktop Support
- Cards: 3 column layout
- Max width: 1400px (center-aligned)
- Optimized spacing and margins

---

## 7. Accessibility

### 7.1 Keyboard Navigation
- Access all interactive elements with Tab key
- Click buttons with Enter/Space
- Close modals/dropdowns with Esc key

### 7.2 Screen Reader Support
- Use appropriate ARIA labels
- Use semantic HTML (header, nav, main, section, article, etc.)
- Provide alt text (images, icons)

### 7.3 Color Contrast
- Comply with WCAG AA standards (4.5:1 or higher)
- Ensure sufficient contrast between text and background
- Do not convey information with color alone (use text, icons together)

---

## 8. Animation

### 8.1 Transition Effects

| Effect | Duration | Usage |
|--------|----------|-------|
| **Page Transition** | 300ms (Fade) | Page-to-page navigation |
| **Card Hover** | 200ms (Shadow increase) | Card hover |
| **Button Click** | 100ms (Scale) | Button click |

### 8.2 Loading Animation
- **Spinner**: Rotation animation
- **Skeleton UI**: Pulse effect

### 8.3 Principles
- Animations should be fast and natural
- Avoid excessive animations
- Design to not interfere with user experience

---

## 9. Icons

### 9.1 Icon Library
- Material Icons or Heroicons
- Use consistent icon style
- Unify outline or filled style

### 9.2 Main Icons

| Icon | Usage |
|------|-------|
| **Refresh** | Refresh button |
| **Settings** | Settings page |
| **Compare** | Comparison functionality |
| **Chart** | Chart display |
| **Arrow Up/Down** | Rise/fall display |
| **Menu** | Mobile menu |
| **Sun** | Light mode indicator / theme toggle |
| **Moon** | Dark mode indicator / theme toggle |

---

## 10. Dark Mode Implementation Guidelines

### 10.1 Technical Implementation
- **CSS Variables**: Use CSS custom properties for all color values
- **Class-based Toggle**: Add/remove `dark` class to root element (html/body)
- **State Management**: Store theme preference in localStorage
- **System Preference**: Detect and respect `prefers-color-scheme` media query on initial load

### 10.2 Component Adaptation
- All components must support both light and dark modes
- Use semantic color tokens (e.g., `--color-background`, `--color-text-primary`) instead of hardcoded colors
- Test all interactive states (hover, active, focus) in both themes

### 10.3 Chart and Data Visualization
- Charts must adapt colors for dark mode
- Ensure data points remain visible and distinguishable
- Use appropriate color schemes for different chart types

### 10.4 Testing Requirements
- Visual regression testing for both themes
- Accessibility testing (contrast ratios) in both modes
- Cross-browser compatibility verification
- Performance testing for theme transition animations

---

