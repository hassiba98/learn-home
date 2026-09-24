"""Single source of truth for the Learn@Home delivery Kanban (Trello board + KANBAN.md)."""

BOARD_URL = "https://trello.com/b/AQi45ICp/learnhome-delivery-board-user-stories"
FUNCTIONAL_BOARD_URL = "https://trello.com/b/2lXr3ret/learnhome-website-project"

# Trello short links of each card (https://trello.com/c/<short>)
LINKS = {
    "README": "fNnWtWAQ", "QUESTIONS": "1IgqZ7MA",
    "EN-01": "J3nnZnae",
    "US-01": "jP0SNbZu", "US-02": "6zpG0zaB", "US-03": "3OUMsbTY", "US-04": "N9p7OIYh",
    "US-05": "4iWti71s", "US-06": "5sFSxo39", "US-07": "Avxd1ueY", "US-08": "MIN2KBjK",
    "US-09": "d42rg07h", "US-10": "8iU5i7Jb", "US-11": "AGUa2O4v",
    "US-12": "dmnQ7KxL", "US-13": "3XE0Mj9A", "US-14": "EDY1wLXp",
    "US-15": "uJETs0om", "US-16": "Gkx8gA8a",
}


def url(key):
    return f"https://trello.com/c/{LINKS[key]}"


LISTS = [
    "📘 Read me & Client questions",
    "Backlog (Should / later)",
    "⛔ Blocked (waiting on dependencies)",
    "✅ Ready for Dev",
    "In Progress",
    "Code Review / QA (Gherkin tests)",
    "Done",
]

# Label colours (Trello labels) = functional block (epic)
EPIC_COLOR = {
    "Authentication": "green", "Dashboard": "blue",
    "Chat": "purple", "Calendar": "yellow", "Task management": "orange",
}

TICKETS = [
    dict(
        key="EN-01", title="Foundation: domain, hosting, HTTPS and Python project setup",
        epic="Foundation", actor="Dev team", priority="Must", uc="-", wireframes="All (shared header/menu)",
        sprint=1, list="✅ Ready for Dev",
        story=("First ticket to do. Prepare the ground before coding the Learn@Home website in Python: "
               "domain name, hosting, HTTPS, project skeleton, and the user base shared by all the other tickets."),
        checklists={
            "1. Domain, hosting & security": [
                "Choose and reserve the domain name (e.g. learnathome.org) with a registrar (OVH, Gandi...)",
                "Choose the hosting for a Python web app (PaaS like Render / Scalingo, or a VPS)",
                "Configure the DNS records so the domain points to the host",
                "Enable HTTPS: SSL/TLS certificate (Let's Encrypt, auto-renewal) + redirect HTTP to HTTPS",
                "Create the database (PostgreSQL) on the host",
                "Choose an email sending service (needed by US-03 password reset) and configure SPF / DKIM on the domain",
                "Legal basics: legal notice + privacy policy (GDPR, the site handles minors' data)",
            ],
            "2. Python project setup": [
                "Git repository + branch strategy (main / develop / feature branches)",
                "Python version, virtual environment and requirements file",
                "Web framework chosen (e.g. Django) and project skeleton created",
                "Secrets and settings in environment variables (.env never committed)",
                "Dev, staging and production environments",
                "Test runner with Gherkin support (behave / pytest-bdd) + linter",
                "CI: tests run on every push, automatic deployment to staging",
                "A first 'Hello Learn@Home' page is online on the domain, over HTTPS",
            ],
            "3. Base for the user stories": [
                "User model: first name, last name, email, hashed password, role (Student / Volunteer)",
                "'Follows' link: a student has one volunteer, a volunteer follows several students",
                "Shared page layout: header, menu (Dashboard, Chat, Calendar, Tasks), place for the Log out button",
                "Test data: 1 volunteer, 2 followed students, 1 student not followed",
            ],
        },
        ac=[],
        gherkin="""Feature: Foundation
  Scenario: The site is online and secure
    When I open http://<domain>
    Then I am redirected to https://<domain>
    And I see the Learn@Home home page""",
        blocked_by=[], blocks=["US-01", "US-02", "US-14", "US-16"], relates=["QUESTIONS"],
        note="Start with this ticket: every other ticket depends on it directly or indirectly.",
    ),
    dict(
        key="US-01", title="Create an account", epic="Authentication", actor="Visitor", priority="Must",
        uc="UC-01", wireframes="1. Login, 2. Create account", sprint=1, list="✅ Ready for Dev",
        story="As a visitor, I want to create an account with my email and a password, so that I can access the Learn@Home platform.",
        ac=[
            'AC1. The login page contains a "Create an account" link that opens the account creation page.',
            "AC2. The form contains: first name, last name, email, password, password confirmation and role (Student or Volunteer). All fields are mandatory.",
            "AC3. The email must have a valid format and must not already be used by another account.",
            "AC4. The password must contain at least 8 characters, including at least one letter and one number, and both password fields must match.",
            "AC5. When the account is created, the user is redirected to the login page with a success message.",
        ],
        gherkin="""Feature: Create an account
  Scenario: Successful account creation
    Given I am on the account creation page
    When I fill in all mandatory fields with valid data
    And I click on "Create my account"
    Then my account is created
    And I am redirected to the login page with the message "Your account has been created"

  Scenario: Email already used
    Given an account already exists with the email "jean.dupont@mail.com"
    When I try to create an account with the email "jean.dupont@mail.com"
    Then I see the error message "This email is already in use"
    And no account is created""",
        blocked_by=["EN-01"], blocks=["US-03"], relates=["US-02"],
        note="Can start in parallel with EN-01 (form + validation rules), then plugs into the User model once EN-01 is merged.",
    ),
    dict(
        key="US-02", title="Log in (+ protected pages)", epic="Authentication", actor="Visitor", priority="Must",
        uc="UC-02", wireframes="1. Login", sprint=1, list="✅ Ready for Dev",
        story="As a visitor who has an account, I want to log in with my email and password, so that I can access my personal space.",
        ac=[
            'AC1. The login page contains an Email field, a Password field, a "Log in" button, a "Forgot password?" link and a "Create an account" link.',
            "AC2. With valid credentials, the user is redirected to his dashboard.",
            "AC3. With invalid credentials, a generic error message is displayed, without saying which field is wrong.",
            "AC4. All pages except the login, account creation and password recovery pages are only accessible when logged in. Otherwise the user is redirected to the login page.",
        ],
        gherkin="""Feature: Log in
  Scenario: Successful login
    Given I have an account with the email "clarisse.roger@mail.com"
    And I am on the login page
    When I enter my email and my correct password
    And I click on "Log in"
    Then I am redirected to my dashboard

  Scenario: Wrong password
    Given I am on the login page
    When I enter my email and a wrong password
    And I click on "Log in"
    Then I see the message "Incorrect email or password"
    And I stay on the login page

  Scenario: Access a protected page without being logged in
    Given I am not logged in
    When I try to open the Chat page
    Then I am redirected to the login page""",
        blocked_by=["EN-01"], blocks=["US-03", "US-04", "US-05", "US-10", "US-12", "US-15"], relates=["US-01"],
        note="Critical path: 6 tickets wait for this one. Until US-05 exists, AC2 redirects to a temporary empty dashboard page.",
    ),
    dict(
        key="US-03", title="Recover forgotten password", epic="Authentication", actor="Visitor, Email Service", priority="Must",
        uc="UC-03", wireframes="1. Login, 3. Forgot password", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a visitor who forgot my password, I want to receive a reset link by email, so that I can choose a new password and access my account again.",
        ac=[
            'AC1. The "Forgot password?" link on the login page opens a page where the user enters his email.',
            "AC2. If the email matches an account, the Email Service sends a password reset link to this address.",
            "AC3. The same neutral confirmation message is displayed whether or not the email exists (for security).",
            "AC4. The reset link is valid for 24 hours and can only be used once.",
            "AC5. The new password must follow the same rules as in US-01. After the reset, the user is redirected to the login page.",
        ],
        gherkin="""Feature: Recover forgotten password
  Scenario: Request a reset link
    Given I have an account with the email "jean.dupont@mail.com"
    And I am on the "Forgot password" page
    When I enter "jean.dupont@mail.com" and click on "Send"
    Then a reset link is sent to "jean.dupont@mail.com"
    And I see the message "If this email exists, a reset link has been sent"

  Scenario: Expired reset link
    Given I received a reset link more than 24 hours ago
    When I open this link
    Then I see the message "This link has expired"
    And I can request a new link""",
        blocked_by=["US-01", "US-02"], blocks=[], relates=[],
        note="Needs the password rules of US-01 and the login page of US-02. Also needs an email-sending service (external actor 'Email Service').",
    ),
    dict(
        key="US-04", title="Log out", epic="Authentication", actor="Registered User", priority="Must",
        uc="UC-04", wireframes="4 to 8 (header)", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to log out, so that nobody else can access my account from the same device.",
        ac=[
            'AC1. A "Log out" button is visible on every page when the user is logged in.',
            "AC2. Clicking on it ends the session and redirects the user to the login page.",
            "AC3. After logging out, protected pages are no longer accessible (including with the browser's back button).",
        ],
        gherkin="""Feature: Log out
  Scenario: Log out
    Given I am logged in
    When I click on "Log out"
    Then my session is closed
    And I am redirected to the login page

  Scenario: Protected page after logging out
    Given I have just logged out
    When I click on the browser's back button
    Then I am redirected to the login page""",
        blocked_by=["US-02"], blocks=[], relates=["EN-01"],
        note="The button lives in the shared header created in EN-01.",
    ),
    dict(
        key="US-05", title="View my dashboard (page + menu)", epic="Dashboard", actor="Registered User", priority="Must",
        uc="UC-05", wireframes="4. Dashboard", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to see a dashboard when I log in, so that I get an overview of my important information at a glance.",
        ac=[
            "AC1. The dashboard is the first page displayed after a successful login.",
            "AC2. It always displays three blocks: my to-do list (US-06), my upcoming appointments (US-07) and my unread messages counter (US-08).",
            "AC3. A menu gives access to the Chat, Calendar and Task management pages.",
        ],
        gherkin="""Feature: View my dashboard
  Scenario: Dashboard displayed after login
    Given I am on the login page
    When I log in with valid credentials
    Then the dashboard is displayed
    And I see my to-do list, my upcoming appointments and my unread messages counter""",
        blocked_by=["US-02"], blocks=["US-06", "US-07", "US-08"], relates=[],
        note="Delivers the page and its 3 empty blocks; their content comes from US-06, US-07 and US-08.",
    ),
    dict(
        key="US-06", title="Dashboard: view to-do list (tasks)", epic="Dashboard", actor="Registered User", priority="Must",
        uc="UC-06", wireframes="4. Dashboard", sprint=3, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to see my tasks to do on my dashboard, so that I know what I have to do next.",
        ac=[
            "AC1. The block lists the tasks that are not done yet, sorted by due date (closest first).",
            'AC2. A maximum of 5 tasks is displayed, with a "See all" link to the Task management page.',
            "AC3. Overdue tasks are highlighted.",
            'AC4. If there is no task to do, the message "No task to do" is displayed.',
        ],
        gherkin="""Feature: View to-do list (tasks)
  Scenario: Tasks to do are displayed
    Given I have 3 tasks that are not done
    When I open my dashboard
    Then I see these 3 tasks sorted by due date

  Scenario: No task to do
    Given all my tasks are done
    When I open my dashboard
    Then I see the message "No task to do\"""",
        blocked_by=["US-05", "US-15"], blocks=[], relates=["US-16"],
        note='Tasks assigned by a volunteer (US-16) must also appear here, with "Assigned by".',
    ),
    dict(
        key="US-07", title="Dashboard: view upcoming appointments", epic="Dashboard", actor="Registered User", priority="Must",
        uc="UC-07", wireframes="4. Dashboard", sprint=3, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to see my upcoming appointments on my dashboard, so that I don't miss a tutoring session.",
        ac=[
            "AC1. The block lists my events and appointments of the next 7 days, in chronological order.",
            "AC2. Each item shows the date, the time, the title and the other participant.",
            'AC3. A link opens the Calendar page. If there is no appointment, the message "No upcoming appointment" is displayed.',
        ],
        gherkin="""Feature: View upcoming appointments
  Scenario: Upcoming appointment displayed
    Given I have an appointment tomorrow at 5:00 pm with "Jean Dupont"
    When I open my dashboard
    Then I see this appointment with its date, time and participant

  Scenario: Appointment too far in the future
    Given my only appointment is in 10 days
    When I open my dashboard
    Then I see the message "No upcoming appointment\"""",
        blocked_by=["US-05", "US-12"], blocks=[], relates=["US-14", "QUESTIONS"],
        note="Until US-14 exists, appointments come from test data.",
    ),
    dict(
        key="US-08", title="Dashboard: unread messages counter", epic="Dashboard", actor="Registered User", priority="Must",
        uc="UC-08", wireframes="4. Dashboard", sprint=4, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to see how many messages I have not read, so that I know if someone is waiting for my answer.",
        ac=[
            "AC1. The counter shows the total number of unread messages, all conversations included.",
            "AC2. It is updated automatically when a new message arrives and when I read messages, without reloading the page.",
            "AC3. Clicking on the counter opens the Chat page.",
        ],
        gherkin="""Feature: View unread messages counter
  Scenario: New message received
    Given my unread messages counter shows 0
    When a contact sends me a message
    Then the counter shows 1 without reloading the page

  Scenario: Messages read
    Given my counter shows 2 unread messages from "Jean Dupont"
    When I open my conversation with "Jean Dupont"
    Then the counter shows 0""",
        blocked_by=["US-05", "US-09"], blocks=[], relates=[],
        note="Reuses the read/unread status and the real-time mechanism built in US-09.",
    ),
    dict(
        key="US-09", title="Send and read instant messages", epic="Chat", actor="Registered User", priority="Must",
        uc="UC-09", wireframes="5. Chat", sprint=3, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to exchange instant messages with my contacts, so that I can communicate directly on the site instead of WhatsApp or SMS.",
        ac=[
            "AC1. The Chat page shows the list of my conversations on the left and the selected conversation on the right.",
            "AC2. Each message shows the sender's profile picture, his name, the timestamp and a read / unread indicator.",
            "AC3. A sent message appears instantly for the recipient, without reloading the page.",
            "AC4. An empty message cannot be sent.",
            "AC5. When the recipient opens the conversation, the messages are marked as read.",
        ],
        gherkin="""Feature: Send and read instant messages
  Scenario: Send a message
    Given I am in my conversation with "Jean Dupont"
    When I type "Hello, did you finish your homework?"
    And I click on the send button
    Then the message appears in the conversation with my profile picture and the timestamp
    And "Jean Dupont" receives it instantly

  Scenario: Message marked as read
    Given I sent a message to "Jean Dupont"
    When "Jean Dupont" opens our conversation
    Then my message is shown as read

  Scenario: Empty message
    Given I am in a conversation
    When I click on the send button without typing anything
    Then no message is sent""",
        blocked_by=["US-10"], blocks=["US-08", "US-11"], relates=["QUESTIONS"],
        note="A conversation only exists once a contact is added (US-10 AC2). Profile picture: see client question Q3.",
    ),
    dict(
        key="US-10", title="Manage contacts (add / delete)", epic="Chat", actor="Registered User", priority="Must",
        uc="UC-10", wireframes="5. Chat", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to add and delete contacts, so that my contact list only contains the people I work with.",
        ac=[
            'AC1. The "+" button opens a search field to find a registered user by name or email.',
            "AC2. Adding a contact creates a new conversation in my list.",
            "AC3. I cannot add myself or a contact that is already in my list.",
            "AC4. Deleting a contact asks for a confirmation, then removes the contact from my list.",
        ],
        gherkin="""Feature: Manage contacts (add / delete)
  Scenario: Add a contact
    Given I am on the Chat page
    When I click on "+" and search for "Clarisse Roger"
    And I select "Clarisse Roger" in the results
    Then "Clarisse Roger" appears in my conversation list

  Scenario: Delete a contact
    Given "Clarisse Roger" is in my contact list
    When I choose "Delete contact" and confirm
    Then "Clarisse Roger" no longer appears in my conversation list""",
        blocked_by=["US-02"], blocks=["US-09"], relates=["QUESTIONS"],
        note="First Chat ticket: it creates the Chat page and the conversation list. Search scope (all users or only the assigned volunteer/students?): see client question Q4.",
    ),
    dict(
        key="US-11", title="View chat history", epic="Chat", actor="Registered User", priority="Must",
        uc="UC-11", wireframes="5. Chat", sprint=4, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to scroll back through my past messages, so that I can find information that was shared earlier.",
        ac=[
            "AC1. When a conversation is opened, the 50 most recent messages are displayed.",
            "AC2. Scrolling up loads older messages.",
            "AC3. Messages are displayed in chronological order, with a separator for each day.",
        ],
        gherkin="""Feature: View chat history
  Scenario: Load older messages
    Given my conversation with "Jean Dupont" contains 120 messages
    When I open the conversation
    Then I see the 50 most recent messages
    When I scroll up to the top of the conversation
    Then older messages are loaded""",
        blocked_by=["US-09"], blocks=[], relates=[],
        note="",
    ),
    dict(
        key="US-12", title="View my calendar", epic="Calendar", actor="Registered User", priority="Must",
        uc="UC-12", wireframes="6. Calendar", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to see my events and appointments in a calendar, so that I can organise my week.",
        ac=[
            "AC1. The calendar opens on the current week. The user can switch to a day, week or month view.",
            "AC2. The user can navigate to the previous or next period. Today is highlighted.",
            "AC3. Each event shows its time and title. The user only sees his own events and appointments.",
        ],
        gherkin="""Feature: View my calendar
  Scenario: Display the current week
    Given I have an appointment on Wednesday at 5:00 pm
    When I open the Calendar page
    Then I see the current week
    And my appointment is displayed on Wednesday at 5:00 pm

  Scenario: Switch to month view
    Given I am on the Calendar page
    When I select the "Month" view
    Then all my events of the current month are displayed""",
        blocked_by=["US-02"], blocks=["US-07", "US-13", "US-14"], relates=[],
        note="Creates the Appointment data (title, date, start/end time, participants, description), filled with seed data until US-14 is done.",
    ),
    dict(
        key="US-13", title="View appointment details", epic="Calendar", actor="Registered User", priority="Must",
        uc="UC-13", wireframes="6. Calendar", sprint=3, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to click on an appointment to see its details, so that I know exactly what is planned.",
        ac=[
            "AC1. Clicking on an event opens a detail window with the title, date, start and end time, participants and description.",
            "AC2. Closing the window brings the user back to the calendar.",
        ],
        gherkin="""Feature: View appointment details
  Scenario: Open appointment details
    Given I have an appointment "Maths homework" with "Jean Dupont"
    When I click on this appointment in my calendar
    Then I see its title, date, start and end time, participants and description""",
        blocked_by=["US-12"], blocks=[], relates=[],
        note="",
    ),
    dict(
        key="US-14", title="Schedule an appointment with a student (volunteer)", epic="Calendar", actor="Volunteer", priority="Should",
        uc="UC-14", wireframes="6. Calendar, 7. New appointment", sprint=4, list="Backlog (Should / later)",
        story="As a volunteer, I want to schedule an appointment with one of my students, so that we can plan our weekly tutoring session.",
        ac=[
            'AC1. Only volunteers see the "New appointment" button.',
            "AC2. The student list only contains the students followed by the volunteer.",
            "AC3. Mandatory fields: student, title, date, start time and end time. The end time must be after the start time and the date cannot be in the past.",
            "AC4. Once saved, the appointment appears in the calendar of the volunteer and of the student, and on their dashboards.",
        ],
        gherkin="""Feature: Schedule an appointment with a student
  Scenario: Successful scheduling
    Given I am logged in as a volunteer following "Jean Dupont"
    When I create an appointment with "Jean Dupont" next Monday from 5:00 pm to 5:30 pm
    Then the appointment appears in my calendar
    And it appears in the calendar of "Jean Dupont"

  Scenario: A student cannot schedule an appointment
    Given I am logged in as a student
    When I open the Calendar page
    Then I do not see the "New appointment" button""",
        blocked_by=["US-12", "EN-01"], blocks=[], relates=["US-07", "QUESTIONS"],
        note="Only way to create appointments: we recommend raising it to Must (client question Q2).",
    ),
    dict(
        key="US-15", title="Create and manage my own tasks", epic="Task management", actor="Registered User", priority="Must",
        uc="UC-15", wireframes="8. Task management", sprint=2, list="⛔ Blocked (waiting on dependencies)",
        story="As a registered user, I want to create, view, update and mark my tasks as done, so that I stay organised in my work.",
        ac=[
            "AC1. A task has a title (mandatory), a description (optional) and a due date (mandatory).",
            "AC2. A task created with this feature is automatically assigned to its creator: a student can only create tasks for himself.",
            "AC3. My tasks are listed by due date. I can edit or delete the tasks I created.",
            'AC4. I can mark any of my tasks as done (including tasks assigned by my volunteer): it moves to the "Done" section.',
            "AC5. A student cannot edit or delete a task created by his volunteer.",
        ],
        gherkin="""Feature: Create and manage my own tasks
  Scenario: A student creates a task for himself
    Given I am logged in as a student
    When I create a task "Read chapter 3" due on Friday
    Then the task appears in my task list
    And it is assigned to me

  Scenario: Mark a task as done
    Given I have a task "Read chapter 3" to do
    When I mark it as done
    Then it moves to the "Done" section

  Scenario: A student cannot assign a task to someone else
    Given I am logged in as a student
    When I create a task
    Then no field allows me to choose another assignee""",
        blocked_by=["US-02"], blocks=["US-06", "US-16"], relates=[],
        note="Creates the Task data (title, description, due date, creator, assignee, done).",
    ),
    dict(
        key="US-16", title="Create a task for a followed student (volunteer)", epic="Task management", actor="Volunteer", priority="Must",
        uc="UC-16", wireframes="8. Task management", sprint=3, list="⛔ Blocked (waiting on dependencies)",
        story="As a volunteer, I want to create a task for one of my students, so that I can guide their work between our sessions.",
        ac=[
            "AC1. When a volunteer creates a task, he can choose the assignee among himself and the students he follows only.",
            'AC2. The task appears in the student\'s task list and dashboard, with the mention "Assigned by" followed by the volunteer\'s name.',
            "AC3. The volunteer can see whether the task is done.",
        ],
        gherkin="""Feature: Create a task for a followed student
  Scenario: Assign a task to a followed student
    Given I am logged in as a volunteer following "Jean Dupont"
    When I create a task "Exercise 5 page 42" for "Jean Dupont" due on Thursday
    Then the task appears in the task list of "Jean Dupont"
    And it shows "Assigned by" with my name

  Scenario: Student not followed
    Given I am logged in as a volunteer who does not follow "Lucas Martin"
    When I create a task
    Then "Lucas Martin" is not in the list of possible assignees""",
        blocked_by=["US-15", "EN-01"], blocks=[], relates=["US-06"],
        note="Adds the 'Assign to (volunteer only)' field to the form built in US-15, using the 'follows' link from EN-01.",
    ),
]

QUESTIONS = [
    ("Q1", "Who assigns a volunteer to a student (the 'follows' link)? No administrator actor exists in the use case diagram. Proposal: Learn@Home staff through an admin back-office (new user story).", ["EN-01", "US-14", "US-16"]),
    ("Q2", "Appointments can only be created by US-14 (priority Should), but US-07, US-12 and US-13 (Must) display appointments. Proposal: raise US-14 to Must.", ["US-14", "US-07", "US-12"]),
    ("Q3", "The chat shows the sender's profile picture (US-09 AC2), but the account creation form (US-01) has no picture upload. Proposal: default avatar with initials, and picture upload as a later story.", ["US-09", "US-01"]),
    ("Q4", "Contacts (US-10): can a student search and add ANY registered user, or only their volunteer? Proposal (child protection): a student can only add their volunteer; a volunteer can only add the students they follow.", ["US-10"]),
    ("Q5", "Can a volunteer edit or cancel an appointment? Not covered by any user story.", ["US-14"]),
    ("Q6", "The kick-off notes ask for 'a to-do list from the calendar' on the dashboard. We interpreted it as 'upcoming appointments of the next 7 days' (US-07). To confirm.", ["US-07"]),
]

SPRINTS = {
    1: "Foundation + authentication core (the entry point of every other feature)",
    2: "Every feature that only needs a logged-in user: log out, password recovery, dashboard page, contacts, calendar, own tasks",
    3: "Features that build on sprint 2: messaging, appointment details, tasks for students, dashboard blocks (tasks, appointments)",
    4: "Features that build on sprint 3: unread counter, chat history, + US-14 (Should)",
}
