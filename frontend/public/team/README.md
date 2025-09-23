# Team Photos

This directory contains team member photos for the Nimo platform.

## Current Setup

✅ **Local Images**: Actual team photos downloaded and stored locally (JPG format)
✅ **High Quality**: 400x400px professional photos from GitHub profiles
✅ **Error Handling**: Graceful fallback to initials if images fail to load

## Photo Requirements

- **Size**: 400x400px (square) recommended
- **Format**: JPG, PNG, or SVG
- **Quality**: High resolution, professional headshots preferred
- **Background**: Clean, preferably solid color or subtle gradient

## Current Team Members

### John Koiyaki
- **Local File**: `john-koiyaki.jpg` ✅ **UPDATED** - Actual GitHub profile photo
- **GitHub Source**: Downloaded from `https://avatars.githubusercontent.com/u/polymathuniversata`
- **Role**: Creative Technologist & Lead Developer

### Aisha Omar Farah
- **Local File**: `aisha-omar-farah.jpg` ✅ **UPDATED** - Actual GitHub profile photo
- **GitHub Source**: Downloaded from `https://avatars.githubusercontent.com/u/Aishagojo`
- **Role**: Frontend & Web3 Developer

## Replacing Placeholder Images

To replace the current SVG placeholders with real photos:

1. **Take/Obtain Professional Photos**:
   - Use high-quality headshots
   - Ensure good lighting and neutral backgrounds
   - Save as JPG or PNG format

2. **Replace Files**:
   ```bash
   # Replace John's photo
   cp /path/to/john-photo.jpg ./john-koiyaki.jpg

   # Replace Aisha's photo
   cp /path/to/aisha-photo.jpg ./aisha-omar-farah.jpg
   ```

3. **Update File Extensions**:
   - If using PNG instead of JPG, update the `src` attribute in `LandingPage.tsx`
   - Current: `src="/team/john-koiyaki.svg"`
   - New: `src="/team/john-koiyaki.jpg"`

## GitHub Profile Photo URLs

The system automatically falls back to GitHub profile photos:
- Format: `https://github.com/[username].png?size=400`
- Example: `https://github.com/johnkoiyaki.png?size=400`

## Implementation Details

The team images in `LandingPage.tsx` use a three-tier fallback system:

1. **Primary**: Local image (`/team/[name].svg`)
2. **Secondary**: GitHub profile photo
3. **Tertiary**: Initials fallback (displayed if both image sources fail)

## Adding New Team Members

1. Add photo to this directory: `firstname-lastname.jpg`
2. Update the team section in `frontend/src/pages/LandingPage.tsx`
3. Add GitHub profile link for fallback
4. Update this README with new team member details

## Usage in Code

```tsx
// Current implementation with fallbacks
<img
  src="/team/john-koiyaki.svg"
  alt="John Koiyaki"
  className="w-16 h-16 rounded-full object-cover shadow-md"
  onError={(e) => {
    const target = e.target as HTMLImageElement;
    target.src = 'https://github.com/username.png?size=160';
    target.onerror = () => {
      target.style.display = 'none';
      // Show initials fallback
    };
  }}
/>
```