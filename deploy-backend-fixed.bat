@echo off
echo Deploying backend with static file serving fix...

cd inmuebles-backend

echo Checking status...
git status

echo Adding files...
git add .

echo Committing changes...
git commit -m "Fix static file serving and upload endpoints"

echo Force pushing to GitHub...
git push --force origin main

echo Deployment triggered!
echo Check Render dashboard for deployment status.
echo Photos should be visible once deployment completes.

pause