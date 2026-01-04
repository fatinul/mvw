# Create an issue on github
gh issue create --title "Add dark mode toggle" --body "Drafting the UI for theme switching" --assignee @me
gh issue create # interactive

# Open the issue branch
gh issue develop <number> --checkout

# Create a pull request
gh pr create --fill --web

# See closed issue
gh issue list --state closed
