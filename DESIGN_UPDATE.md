# CUHK Label Generator - Design Update

## 🎨 New Visual Design

The Label Generator web platform has been redesigned with an elegant purple and gold color scheme that reflects CUHK's prestigious brand identity.

### Color Palette

#### Purple Variants
- **Classic Purple** (`#764393`) - Primary brand color
- **Royal Purple** (`#5E3676`) - Deeper, richer purple for headers
- **Dynamic Purple** (`#7D2882`) - Vibrant accent
- **Milky Purple** (`#F1ECF4`) - Soft background
- **Dewy Purple** (`#D5C5DE`) - Light accent

#### Gold Variants
- **Champagne Gold** (`#F1EBDE`) - Elegant light gold
- **Classic Gold** (`#DFD0AA`) - Warm gold
- **Royal Gold** (`#84754E`) - Rich gold for accents
- **Dynamic Gold** (`#F0AA23`) - Bright gold for CTAs

### Design Features

#### 1. **Gradient Backgrounds**
- Subtle gradient from milky purple to champagne gold creates depth
- Card hover effects with smooth transitions
- Purple-to-purple gradients on buttons and headers

#### 2. **Modern Card Design**
- Elevated cards with soft shadows
- Purple gradient headers with gold accent borders
- Glass-morphism effect with backdrop blur
- Hover animations that lift cards

#### 3. **Button Styling**
- Primary buttons: Purple gradient with shadow
- Success buttons: Gold gradient
- Info buttons: Amethyst/Lilac gradient
- Smooth hover effects with transform and shadow changes

#### 4. **Form Elements**
- Purple-tinted borders
- Focus states with purple glow
- Custom checkbox styling with purple checkmarks
- Enhanced multi-select dropdowns

#### 5. **Typography**
- Royal purple for headings
- Mauve for body text
- Strong contrast for readability
- Text shadows for depth

#### 6. **Interactive Elements**
- Smooth transitions on all interactive elements
- Custom scrollbar with purple gradient
- Loading states with purple spinners
- Animated success/error messages

### Usage

The new design is automatically applied when you access the web interface:

```bash
source .venv/bin/activate
python run_web.py --port 8002
```

Then open your browser to: `http://localhost:8002`

### Files Modified

- `static/css/main.css` - Complete redesign with purple & gold theme
- `templates/index.html` - Updated with new header, icons, and footer
- `colors.css` - Color palette reference file

### Design Principles

1. **Elegance** - Refined gradients and smooth transitions
2. **Professionalism** - Clean layout with clear hierarchy
3. **Brand Consistency** - CUHK purple and gold throughout
4. **User Experience** - Intuitive interface with visual feedback
5. **Accessibility** - High contrast ratios for readability

### Preview

The platform now features:
- 🏛️ Elegant header with CUHK branding
- 📤 Clear step-by-step workflow
- ⚙️ Beautiful configuration interface
- 🎯 Professional label generation
- 📊 Stylish data export options

### Customization

To adjust colors, edit the CSS variables in `static/css/main.css`:

```css
:root {
  --classic-purple: #764393;
  --royal-gold: #84754E;
  /* ... other colors */
}
```

---

**The Label Generator is now ready for launch with a polished, professional appearance that reflects CUHK's prestigious identity.** 🎓✨
