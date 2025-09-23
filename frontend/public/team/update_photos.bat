@echo off
REM Team Photo Update Script for Windows
REM This script helps replace placeholder team images with real photos

echo 🖼️  Nimo Team Photo Update Script
echo =================================

echo.
echo Usage examples:
echo ---------------
echo # Update John's photo
echo copy "C:\path\to\john-professional-photo.jpg" "john-koiyaki.jpg"
echo.
echo # Update Aisha's photo
echo copy "C:\path\to\aisha-professional-photo.jpg" "aisha-omar-farah.jpg"
echo.
echo Current team members:
echo - john-koiyaki
echo - aisha-omar-farah
echo.
echo 📁 Place your photos in this directory and run the copy commands above.
echo 📝 Remember to update the file extension in LandingPage.tsx if using JPG instead of SVG
echo    Change: src="/team/john-koiyaki.svg"
echo    To:     src="/team/john-koiyaki.jpg"
echo.
pause