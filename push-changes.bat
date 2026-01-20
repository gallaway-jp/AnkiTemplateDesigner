@echo off
cd /d "D:\Development\Python\AnkiTemplateDesigner"
echo Pushing changes to repository...
git add .
git commit -m "Phase 4.5 Complete: Release and Distribution - Addon ready for immediate launch"
git push
echo Changes pushed successfully!
pause
