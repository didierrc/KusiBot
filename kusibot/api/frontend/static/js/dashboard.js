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
        div_messages = []
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

async function getAssessmentsHistory(userId) {

    try {
        // Fetch assessment history
        const response = await fetch(`${DASHBOARD_URL}assessments?user_id=${userId}`)
        if (!response.ok)
            throw new Error(`HTTP error. Status: ${response.status}`)

        const data = await response.json()

        if (!data.assessments || data.assessments.length === 0) {
            const pNoAssessments = document.createElement('p')
            pNoAssessments.innerHTML = 'No assessments found'
            return [pNoAssessments]
        }

        // Create assessments divs
        div_assessments = []
        for (const assessment of data.assessments) {
            const assessmentAccordion = document.createElement('div')
            assessmentAccordion.classList.add('accordion-item')

            const assessmentHeader = document.createElement('h2')
            assessmentHeader.classList.add('accordion-header')
            assessmentHeader.id = `assesmentHeading-${assessment.id}`

            const assessmentButton = document.createElement('button')
            assessmentButton.classList.add('accordion-button')
            assessmentButton.classList.add('collapsed')
            assessmentButton.setAttribute('type', 'button')
            assessmentButton.setAttribute('data-bs-toggle', 'collapse')
            assessmentButton.setAttribute('data-bs-target', `#collapseAssesment-${assessment.id}`)
            assessmentButton.setAttribute('aria-expanded', 'false')
            assessmentButton.setAttribute('aria-controls', `collapseAssesment-${assessment.id}`)

            const assessmentStrong = document.createElement('strong')
            assessmentStrong.textContent = assessment.assessment_type
            assessmentButton.appendChild(assessmentStrong)
            assessmentButton.appendChild(document.createTextNode(` - ${new Date(assessment.start_time).toLocaleString()}`))

            const assessmentBadge = document.createElement('span')
            assessmentBadge.classList.add('badge')
            assessmentBadge.classList.add('bg-secondary')
            assessmentBadge.classList.add('ms-2')
            assessmentBadge.textContent = `Interpretation: ${assessment.interpretation}`
            assessmentButton.appendChild(assessmentBadge)

            assessmentHeader.appendChild(assessmentButton)
            assessmentAccordion.appendChild(assessmentHeader)

            const assessmentCollapse = document.createElement('div')
            assessmentCollapse.id = `collapseAssesment-${assessment.id}`
            assessmentCollapse.classList.add('accordion-collapse')
            assessmentCollapse.classList.add('collapse')
            assessmentCollapse.setAttribute('aria-labelledby', `assesmentHeading-${assessment.id}`)
            assessmentCollapse.setAttribute('data-bs-parent', '#assessmentsAccordion')

            const assessmentBody = document.createElement('div')
            assessmentBody.classList.add('accordion-body')
            assessmentBody.textContent = `Fetching assessment details...`

        }

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
        assessmentsAccordion.innerHTML = ''
        assessmentsAccordion.append(...await getAssessmentsHistory(userId))
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