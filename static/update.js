let allGoals = ['Goal 1', 'Objective 1', 'Objective 2', 'Objective 3', 'Goal 2', 'Objective 4', 'Objective 5', 'Objective 6', 'Goal 3', 'Objective 7', 'Objective 8', 'Objective 9']
let inputIds = ['Goal 1 input', 'Objective 1 input', 'Objective 2 input', 'Objective 3 input', 'Goal 2 input', 'Objective 4 input', 'Objective 5 input', 'Objective 6 input', 'Goal 3 input', 'Objective 7 input', 'Objective 8 input', 'Objective 9 input']
let allgoalsID = ['Goal 1 ORI', 'Objective 1 ORI', 'Objective 2 ORI', 'Objective 3 ORI', 'Goal 2 ORI', 'Objective 4 ORI', 'Objective 5 ORI', 'Objective 6 ORI', 'Goal 3 ORI', 'Objective 7 ORI', 'Objective 8 ORI', 'Objective 9 ORI', "Info ORI"]
window.onload = function() {
    console.log(document.getElementsByName('update').length)
    for (let i = 0; i < allGoals.length; i ++) {
    document.getElementById(inputIds[i]).value = document.getElementById(allgoalsID[i]).textContent
    }
  }
for (let i = 0; i < allGoals.length; i ++) {
    document.getElementById(allGoals[i]).addEventListener('change', function() {
        if (this.checked) {
            document.getElementById(inputIds[i]).disabled = true
            document.getElementById(inputIds[i]).value = document.getElementById(allgoalsID[i]).textContent
        }
        else {
            document.getElementById(inputIds[i]).disabled = false
        }
    })
}