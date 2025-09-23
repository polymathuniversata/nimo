#!/bin/bash

# Team Photo Update Script
# This script helps replace placeholder team images with real photos

echo "🖼️  Nimo Team Photo Update Script"
echo "================================="

# Function to update a team member's photo
update_team_photo() {
    local name=$1
    local file_path=$2

    if [ -f "$file_path" ]; then
        echo "✅ Found photo for $name: $file_path"
        cp "$file_path" "./$name.jpg"
        echo "✅ Updated $name.jpg"

        # Update LandingPage.tsx if needed
        echo "📝 Remember to update the file extension in LandingPage.tsx if using JPG instead of SVG"
        echo "   Change: src=\"/team/$name.svg\""
        echo "   To:     src=\"/team/$name.jpg\""
    else
        echo "❌ Photo not found: $file_path"
    fi
}

echo ""
echo "Usage examples:"
echo "---------------"
echo "# Update John's photo"
echo "update_team_photo \"john-koiyaki\" \"/path/to/john-professional-photo.jpg\""
echo ""
echo "# Update Aisha's photo"
echo "update_team_photo \"aisha-omar-farah\" \"/path/to/aisha-professional-photo.jpg\""
echo ""
echo "Or run directly:"
echo "./update_team_photos.sh"
echo ""
echo "Current team members:"
echo "- john-koiyaki"
echo "- aisha-omar-farah"
echo ""
echo "📁 Place your photos in this directory and run the update commands above."