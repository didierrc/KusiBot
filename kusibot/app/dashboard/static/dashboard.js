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

async function getConversationHistory(userId) {

    try {

        // Fetch conversation history
        const response = await fetch(`${DASHBOARD_URL}conversations?user_id=${userId}`)
        if (!response.ok)
            throw new Error(`HTTP error. Status: ${response.status}`)

        const data = await response.json()

        if (!data.messages || data.messages.length === 0) {
            const pNoMessages = document.createElement('p')
            pNoMessages.innerHTML = 'No messages found'
            return [pNoMessages]
        }

        // Create messages divs
        let div_messages = []
        for (const message of data.messages) {
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

            div_messages.push(messageDiv)
        }

        return div_messages

    } catch (error) {
        console.error('Error fetching conversation history:', error)
        const pError = document.createElement('p')
        pError.innerHTML = 'Error fetching conversation history'
        return [pError]
    }

}

function getBadgeClassForInterpretation(interpretation) {
    const interpretationLower = interpretation.toLowerCase()

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
        caption.innerHTML = `<strong>Details for ${assessment.assessment_type}</strong> (Score: ${assessment.total_score})`

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

    } else
        assessmentBody.textContent = 'Detailed question data not available for this assessment.';

    // Return the populated accordion body element
    return assessmentBody;
}

async function getAssessmentsHistory(userId) {

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
            assessmentStrong.textContent = assessment.assessment_type
            assessmentButton.appendChild(assessmentStrong)
            assessmentButton.appendChild(document.createTextNode(` - Completed: ${new Date(assessment.end_time).toLocaleString()}`))

            const assessmentBadge = document.createElement('span')
            const badgeClass = getBadgeClassForInterpretation(assessment.interpretation)
            assessmentBadge.className = `badge ${badgeClass} ms-auto`
            assessmentBadge.textContent = `Interpretation: ${assessment.interpretation}`
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

async function updateUserDataArea(userId, userName) {

    // Update Selected User Title
    const selectedUserSpan = document.getElementById('selectedUsername');
    if (selectedUserSpan)
        selectedUserSpan.textContent = userName

    const conversationHistory = document.querySelector('.conversation-history');
    const assessmentsAccordion = document.getElementById('assessmentsAccordion');

    // Fetch Conversations
    if (conversationHistory) {
        document.querySelector('.loadingConversation').classList.remove('d-none')
        conversationHistory.innerHTML = ''
        conversationHistory.append(...await getConversationHistory(userId))
        document.querySelector('.loadingConversation').classList.add('d-none')
    }


    // Populate Assessments (Placeholder Example)
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