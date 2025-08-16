@green-hill-canarias
digital rootssettings
Organization, part of 
green-hill-canarias

 Switch settings context 
Access
Code, planning, and automation
Security
Third-party Access
Integrations
Messages
Archive
General
Organization display name
digital roots
Email (will be public)
zaki@greenhillcanarias.com
Description
URL
https://greenhillcanarias.com/
Social accounts
Link to social profile 1
Link to social profile 2
Link to social profile 3
Link to social profile 4
Location
Billing email (Private)
zaki@greenhillcanarias.com
Gravatar email (Private)
zakibaydoun@msn.com
Sponsors update email (Private)
The developers and organizations that your organization sponsors can send you updates to this email.

Profile picture
@green-hill-canarias

Note: To apply for a publisher verification your organization's profile picture should not be irrelevant, abusive or vulgar. It should not be a default image provided by GitHub.@green-hill-canarias
digital rootssettings
Organization, part of 
green-hill-canarias

 Switch settings context 
Access
Code, planning, and automation
Security
Third-party Access
Integrations
Messages
Archive
General
Organization display name
digital roots
Email (will be public)
zaki@greenhillcanarias.com
Description
URL
https://greenhillcanarias.com/
Social accounts
Link to social profile 1
Link to social profile 2
Link to social profile 3
Link to social profile 4
Location
Billing email (Private)
zaki@greenhillcanarias.com
Gravatar email (Private)
zakibaydoun@msn.com
Sponsors update email (Private)
The developers and organizations that your organization sponsors can send you updates to this email.

Profile picture
@green-hill-canarias

Note: To apply for a publisher verification your organization's profile picture should not be irrelevant, abusive or vulgar. It should not be a default image provided by GitHub.@green-hill-canarias
digital rootssettings
Organization, part of 
green-hill-canarias

 Switch settings context 
Access
Code, planning, and automation
Security
Third-party Access
Integrations
Messages
Archive
General
Organization display name
digital roots
Email (will be public)
zaki@greenhillcanarias.com
Description
URL
https://greenhillcanarias.com/
Social accounts
Link to social profile 1
Link to social profile 2
Link to social profile 3
Link to social profile 4
Location
Billing email (Private)
zaki@greenhillcanarias.com
Gravatar email (Private)
zakibaydoun@msn.com
Sponsors update email (Private)
The developers and organizations that your organization sponsors can send you updates to this email.

Profile picture
@green-hill-canarias

Note: To apply for a publisher verification your organization's profile picture should not be irrelevant, abusive or vulgar. It should not be a default image provided by GitHub.# Organization setup (green-hill-canarias)

Use this checklist to finish moving work into your org and enable bigger Codespaces for ingestion while keeping serve small.

## Links

- Org Codespaces billing: <https://github.com/organizations/green-hill-canarias/settings/codespaces>
- Org Codespaces secrets: <https://github.com/organizations/green-hill-canarias/settings/secrets/codespaces>
- Repo (app): <https://github.com/green-hill-canarias/green-hill-app>
- Repo (digital-roots): <https://github.com/green-hill-canarias/digital-roots>

## 1) Billing and limits

- In org Codespaces settings, set a non-zero spend limit.

## 2) Machine policies (recommendation)

- Create policy "ghc-ingest" (scope: green-hill-app)
  - Allow larger machines (≥ 8 cores, ≥ 16 GB RAM) for ingestion/build.
- Create policy "ghc-serve" (scope: green-hill-app)
  - Allow small/standard machines (2–4 cores, 4–8 GB RAM) for serving/demo.
- Optional: mirror similar policies for digital-roots if needed.

## 3) Secrets

- Add org Codespaces secret: OPENAI_API_KEY
  - Scope: all repositories (or at least green-hill-app and digital-roots)

- Add org/repo secret: ORG_PROJECT_TOKEN (for automation)
  - Create a fine-grained PAT owned by an org admin with scopes: project (read/write), repo (read), issues (write), pull requests (write). Store as an org secret named ORG_PROJECT_TOKEN.
  - Also add ORG_PROJECT_URL as an org/repo secret with your project URL (e.g., <https://github.com/orgs/green-hill-canarias/projects/2>).

## 4) Create Codespaces (billed to org)

- App (ingestion): open green-hill-app → Code → Create codespace on main → pick the large size allowed by policy.
- App (serve): create another codespace on main → pick the small/standard size.
- Digital-roots: repeat if you plan to use Codespaces there.

## 5) After Codespaces start

- Confirm repo remote is org-owned.
- Follow the repo README quick start to run services.

## Notes

- If larger sizes don’t appear, check: (a) you billed to the organization, (b) spend limit > 0, (c) policy allows the size.
