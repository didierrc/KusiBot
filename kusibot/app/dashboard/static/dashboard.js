function searchUserEvent(searchID) {

    const searchInput = document.getElementById(searchID)

    if (searchInput) {

        // If there is input changes...
        searchInput.addEventListener('input', function (e) {

            // Get search term and all user links
            const searchTerm = e.target.value.toLowerCase()
            const userLinks = document.querySelectorAll('.user-select-link')

            // For each user link, if the text content includes the search term, show it, otherwise hide it
            userLinks.forEach(link => {
                const userName = link.textContent.toLowerCase()
                const parentLi = link.parentElement
                if (userName.includes(searchTerm)) {
                    parentLi.style.display = '' // Show if matches
                } else {
                    parentLi.style.display = 'none' // Hide if doesn't match
                }
            })

            // Send the search term to the 
        })
    }
}

function addSearchToSidebars() {
    const searchInputIdDefault = "sidebarSearchInput"
    searchUserEvent(searchInputIdDefault)
    searchUserEvent(`${searchInputIdDefault}Small`)
}


function getBadgeClassForInterpretation(interpretation) {
    const interpretationLower = interpretation ? interpretation.toLowerCase() : 'none'

    if (interpretationLower.includes('severe'))
        return 'bg-danger'
    else if (interpretationLower.includes('moderate'))
        return 'bg-warning text-dark'
    else if (interpretationLower.includes('mild'))
        return 'bg-info text-dark'
    else if (interpretationLower.includes('minimal'))
        return 'bg-success'
    else
        return 'bg-secondary'
}

function createCollapseBodyAssessment(assessment) {

    const assessmentBody = document.createElement('div');
    assessmentBody.classList.add('accordion-body');

    // Check if question data is available
    if (assessment.questions && assessment.questions.length > 0) {

        // Create the table for questions and answers
        const table = document.createElement('table')
        table.className = 'table table-sm table-striped table-hover caption-top'

        // Add Caption
        const caption = table.createCaption()
        caption.innerHTML = `Bot triggered the assesment due to the following user message: "${assessment.message_trigger}"`

        // Create Table Header
        const thead = table.createTHead()
        const headerRow = thead.insertRow()
        const headers = ['#', 'Question', 'User Response', 'Score']
        headers.forEach(text => {
            const th = document.createElement('th')
            th.scope = "col"
            th.textContent = text
            headerRow.appendChild(th)
        })

        // Create Table Body
        const tbody = table.createTBody();
        assessment.questions.forEach(q => {
            const row = tbody.insertRow();
            row.insertCell().textContent = q.question_number ?? '-'
            row.insertCell().textContent = q.question_text ?? 'N/A'
            row.insertCell().textContent = q.user_response ?? '-'
            row.insertCell().textContent = q.categorized_value ?? '-'
        });

        // Append the table to the body
        assessmentBody.appendChild(table)

        // Append total score to the body
        const totalScore = document.createElement('p')
        totalScore.className = 'mt-3'
        totalScore.innerHTML = `<strong>Total Score:</strong> ${assessment.total_score ?? 'Not calculated'}`
        assessmentBody.appendChild(totalScore)

    } else
        assessmentBody.textContent = 'Detailed question data not available for this assessment.';

    // Return the populated accordion body element
    return assessmentBody;
}

async function getAssessmentsHistory(userId) {

    let assesment_date_options = {
        year: '2-digit',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    }

    try {
        // Fetch assessment history
        const response = await fetch(`${DASHBOARD_URL}assessments?user_id=${userId}`)
        if (!response.ok)
            throw new Error(`HTTP error. Status: ${response.status}`)

        const data = await response.json()

        if (!data.assessments || data.assessments.length === 0) {
            const pNoAssessments = document.createElement('p')
            pNoAssessments.innerHTML = 'No assessments found for this user.'
            return [pNoAssessments]
        }

        // Create assessments divs
        let div_assessments = []
        data.assessments.forEach((assessment, index) => {

            const assessmentID = `assessment-${assessment.id || index}`

            // Create main accordion item container
            const assessmentAccordion = document.createElement('div')
            assessmentAccordion.classList.add('accordion-item')

            // Create header for the accordion item
            const assessmentHeader = document.createElement('h2')
            assessmentHeader.classList.add('accordion-header')
            assessmentHeader.id = `heading-${assessmentID}`

            const assessmentButton = document.createElement('button')
            assessmentButton.className = 'accordion-button collapsed'
            assessmentButton.setAttribute('type', 'button')
            assessmentButton.setAttribute('data-bs-toggle', 'collapse')
            assessmentButton.setAttribute('data-bs-target', `#collapse-${assessmentID}`)
            assessmentButton.setAttribute('aria-expanded', 'false')
            assessmentButton.setAttribute('aria-controls', `collapse-${assessmentID}`)

            // Populate the button with assessment details
            const assessmentStrong = document.createElement('strong')
            const asssesmentDate = assessment.end_time ? new Date(assessment.end_time).toLocaleString(undefined, assesment_date_options) : 'Not Finished'
            assessmentStrong.textContent = `${assessment.assessment_type} > ${asssesmentDate}`
            assessmentButton.appendChild(assessmentStrong)

            const assessmentBadge = document.createElement('span')
            const badgeClass = getBadgeClassForInterpretation(assessment.interpretation)
            assessmentBadge.className = `badge ${badgeClass} ms-auto p-2`
            assessmentBadge.textContent = `${assessment.interpretation ? assessment.interpretation : 'No Interpretation'}`
            assessmentButton.appendChild(assessmentBadge)

            assessmentHeader.appendChild(assessmentButton)
            assessmentAccordion.appendChild(assessmentHeader)

            // Create collapse div for the accordion item
            const assessmentCollapse = document.createElement('div')
            assessmentCollapse.id = `collapse-${assessmentID}`
            assessmentCollapse.className = 'accordion-collapse collapse'
            assessmentCollapse.setAttribute('aria-labelledby', `heading-${assessmentID}`)
            assessmentCollapse.setAttribute('data-bs-parent', '#assessmentsAccordion')

            // Adding body to the collapse div
            assessmentCollapse.appendChild(createCollapseBodyAssessment(assessment))
            assessmentAccordion.appendChild(assessmentCollapse)
            div_assessments.push(assessmentAccordion)

        })

        return div_assessments
    } catch (error) {
        console.error('Error fetching assessment history:', error)
        const pError = document.createElement('p')
        pError.innerHTML = 'Error fetching assessment history'
        return [pError]
    }
}

async function getAndDisplayConversationMessages(conversation) {

    // Getting elements to modify
    const conversationHistory = document.querySelector('.conversation-history')
    const loadingIndicator = document.querySelector('.loadingConversation')
    const infoElement = document.getElementById('selectedConversationInfo')

    // Show loading indicator and clear previous messages
    loadingIndicator.classList.remove('d-none')
    infoElement.textContent = `Conversation ID: ${conversation.id} - Created at: ${new Date(conversation.created_at).toLocaleString()} - Finished at: ${conversation.finished_at ? new Date(conversation.finished_at).toLocaleString() : 'Not Finished'}`
    conversationHistory.innerHTML = ''

    // Fetch conversation messages
    try {

        // Fetch conversation history
        const response = await fetch(`${DASHBOARD_URL}conversation_messages?conversation_id=${conversation.id}`)
        if (!response.ok)
            throw new Error(`HTTP error. Status: ${response.status}`)

        const data = await response.json()

        if (!data.messages || data.messages.length === 0) {
            historyContainer.innerHTML = '<p class="text-muted text-center">No messages found for this conversation.</p>'
            return
        }

        // Create and append each message element
        data.messages.forEach(message => {
            const messageDiv = document.createElement('div')
            messageDiv.classList.add('mb-2')
            messageDiv.classList.add('p-2')
            messageDiv.classList.add('rounded')
            messageDiv.classList.add('bg-white')
            messageDiv.classList.add('border')
            messageDiv.classList.add('shadow-sm')

            const messageStrong = document.createElement('strong')

            const messageTimestamp = document.createElement('small')
            messageTimestamp.classList.add('d-block')
            messageTimestamp.classList.add('text-muted')
            messageTimestamp.classList.add('mt-1')
            messageTimestamp.textContent = new Date(message.timestamp).toLocaleString()

            if (message.is_user) {
                messageDiv.classList.add('text-end')
                messageStrong.classList.add('text-secondary')
                messageStrong.textContent = 'User: '
            } else {
                messageStrong.classList.add('text-primary')
                messageStrong.textContent = 'Bot: '
            }

            messageDiv.appendChild(messageStrong)
            messageDiv.appendChild(document.createTextNode(message.text))
            messageDiv.appendChild(messageTimestamp)

            conversationHistory.appendChild(messageDiv)
        })


    } catch (error) {
        console.error('Error fetching conversation messages:', error)
        conversationHistory.innerHTML = '<p class="text-danger text-center">Error fetching conversation history.</p>'
    } finally {
        loadingIndicator.classList.add('d-none')
    }
}

async function populateConversationSelector(userId) {
    const selector = document.getElementById('conversationSelector')
    selector.innerHTML = '' // Clear previous conversations

    try {
        // Fetch conversations for the user
        const response = await fetch(`${DASHBOARD_URL}conversations?user_id=${userId}`)
        if (!response.ok)
            throw new Error('Failed to fetch conversations')

        const data = await response.json()

        if (!data.conversations || data.conversations.length === 0) {
            selector.innerHTML = '<li><a class="dropdown-item disabled" href="#">No conversations found</a></li>'
            document.querySelector('.loadingConversation').classList.add('d-none')
            document.querySelector('.conversation-history').innerHTML = '<p class="text-muted text-center">No conversations found for this user.</p>'
            return
        }

        // Populate the selector with conversations
        data.conversations.forEach(conv => {
            const option = document.createElement('li')
            const link = document.createElement('a')
            link.className = 'dropdown-item'
            link.href = '#'
            link.textContent = `Conv ${conv.id} - ${new Date(conv.created_at).toLocaleString()}`
            link.addEventListener('click', async function (event) {
                event.preventDefault()
                getAndDisplayConversationMessages(conv)

                // Mark the selected conversation as active
                const activeLink = document.querySelector('#conversationSelector .dropdown-item.active')
                if (activeLink) {
                    activeLink.classList.remove('active')
                }
                link.classList.add('active')


            })

            option.appendChild(link)
            selector.appendChild(option)
        })

        // Automatically load the most recent conversation
        if (data.conversations.length > 0) {
            getAndDisplayConversationMessages(data.conversations[0]);
        }

    } catch (error) {
        console.error('Error fetching conversations:', error)
        selector.innerHTML = '<li><a class="dropdown-item disabled" href="#">Error loading conversations</a></li>'
    }
}

async function updateUserDataArea(userId, userName) {

    // Update Selected User Title
    const selectedUserSpan = document.getElementById('selectedUsername');
    if (selectedUserSpan)
        selectedUserSpan.textContent = userName

    // Populate the Conversation selector
    populateConversationSelector(userId)

    // Populate Assessments
    const assessmentsAccordion = document.getElementById('assessmentsAccordion')
    if (assessmentsAccordion) {
        document.querySelector('.loadingAssessments').classList.remove('d-none')
        assessmentsAccordion.innerHTML = ''
        assessmentsAccordion.append(...await getAssessmentsHistory(userId))
        document.querySelector('.loadingAssessments').classList.add('d-none')
    }

}

// Whenever a user is selected, display conversation and assessment data
function addUserSelectionHandling() {

    const userLinks = document.querySelectorAll('.user-select-link')
    const selectUserInfo = document.getElementById('selectUserInfo')
    const userDataArea = document.getElementById('userDataArea')
    const conversationTabButton = document.getElementById('conversationsTab')

    userLinks.forEach(link => {
        link.addEventListener('click', function (event) {

            event.preventDefault()

            // Get user info from data attributes
            const userId = this.dataset.userId
            const userName = this.dataset.userName

            // Mark selected user as active and remove from others
            userLinks.forEach(l => {
                l.classList.remove('active')
                if (l.dataset.userId === userId) {
                    l.classList.add('active')
                }
            })


            // Update data area
            updateUserDataArea(userId, userName)

            // Show data area and User Selection Alert
            if (selectUserInfo) selectUserInfo.classList.add('d-none')
            if (userDataArea) userDataArea.classList.remove('d-none');

            // Show by default the Conversations tab
            if (conversationTabButton) {
                const tab = new bootstrap.Tab(conversationTabButton)
                tab.show()
            }
        })
    })
}

document.addEventListener('DOMContentLoaded', function () {

    // --- Added Search Functionalitiy ---
    addSearchToSidebars()

    // --- User Selection Handling ---
    addUserSelectionHandling()

});