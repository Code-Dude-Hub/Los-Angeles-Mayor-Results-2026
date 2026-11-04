# LA Mayor Election Results — GitHub Pages Edition

A mobile-friendly dark-mode results tracker for the November 3, 2026 Los Angeles mayoral election. It uses the LA County Registrar's official JSON file, not third-party election estimates.

## Upload and launch

1. Create a **public** GitHub repository, e.g. `la-mayor-2026` (do not initialize with extra files if you plan to upload the package with git).
2. Upload all the files and folders from this package to the **root** of the repository, including hidden `.github/workflows/publish.yml`. In GitHub's website interface, you can use *Add file → Upload files*; verify that `.github/workflows/publish.yml` is actually present. Alternatively extract and use Git to push the folder.
3. Go to **Settings → Pages → Build and deployment → Source → GitHub Actions**. Save.
4. Go to **Actions → Update election data and publish site → Run workflow → Run workflow**. The first run fetches county data and deploys the site. If a run fails, open the failed step to see why. Nothing is fabricated.
5. Your site will be at `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/` (unless using a custom domain). GitHub also displays its link under Settings → Pages.

## How Refresh works

- GitHub Actions checks the county feed approximately every **10 minutes** while the workflow is enabled. GitHub does not guarantee exact timing; a scheduled run may be delayed.
- Each successful run validates the election ID, candidate names and vote totals, saves timestamped history to `data/results.json`, and publishes the site through GitHub Pages.
- **Refresh votes** on the website fetches the newly deployed `data/results.json`. It cannot directly start GitHub Actions or force the county to publish a new bulletin.
- When the county has not released a newer count, the button correctly says no newer report. If a county fetch fails, the workflow fails and **does not publish false numbers**; the previous successful site remains available.
- For an immediate county check without waiting for the schedule, open the GitHub repository → Actions → Update election data and publish site → Run workflow. Wait until the run and the Pages deployment complete, then click Refresh votes on your site.
- The page loads the current *published* JSON once when opened, but does not run an ongoing page-side timer. Clicking Refresh checks that published JSON again.

## Total vote count progress (estimated)

The page now adds **Estimated votes counted** and **Estimated remaining**, with a progress bar above the candidate cards. This is different from the candidates' shares of counted votes.

LA County's JSON provides **actual candidate votes**, but not a trustworthy estimate of all ballots that will ultimately be counted in the mayoral race. ABC7's November 3 reporting listed 303,855 votes for Bass and 299,041 votes for Raman (602,896 combined), alongside **51% expected vote reporting**. The site uses that rounded, published estimate to establish an **approximate** denominator of 602,896 / 0.51 ≈ 1,182,149 expected votes, and updates the displayed progress percentage when GitHub publishes more county votes.

**Limitations:** this is not an official LA County vote-count completion percentage or a live AP forecast. The projected final vote total can change over time as turnout information arrives. Accordingly the site uses ≈ and rounds to whole percentages; if the estimated vote total is exceeded, it displays “Estimate needs updating” instead of incorrectly claiming 100%. To update the basis if a credible, newer expected-vote estimate becomes available, change `EXPECTED_REFERENCE` in `index.html`. Source: https://abc7.com/politics/elections/local/

## Important

- The initial `data/results.json` is **empty** on purpose: no unverified election vote totals are preloaded. The first successful workflow populates it.
- Portraits are linked from the official City Council press kit and an official Karen Bass portrait hosted on Wikimedia Commons; they may need local caching if third-party hosts block image hotlinking.
- Pages hosting is static. The source fetch happens in GitHub Actions, so no Windows CMD, local PowerShell server, CORS workaround, or API token in the site is needed.
- **Repository settings:** if `git push` fails in the workflow, confirm workflow permissions allow `contents:write` and branch protection permits GitHub Actions to update the data file.
- Be aware GitHub may disable scheduled workflows in inactive public repositories after an extended period (60 days). You can re-enable them from Actions.

Source: https://www.lavote.gov/home/voting-elections/current-elections/election-results-file-downloads
JSON URL: https://results.lavote.gov/electionresults/json?electionid=4348
