let req = new XMLHttpRequest()
req.onload = function() {
  let result = document.querySelector('#result')
  const data = JSON.parse(req.response)
  result.innerText = data.result
  result.style.color = data.color
}

// run code by clicking button
document.querySelector('#run').addEventListener('click', event => {
  request(event)
})

// run code by pressing Ctrl+Enter
document.addEventListener('keypress', event => {
  if (event.keyCode === 10) {
    request(event)
  }
})

// tab indent in code block
document.querySelector('.textarea').addEventListener('keydown', function(event) {
  if (event.key === 'Tab') {
    event.preventDefault();
    let start = this.selectionStart;
    let end = this.selectionEnd;

    // set textarea value to: text before caret + tab + text after caret
    this.value = this.value.substring(0, start) +
      " " + " " + " " + " " + this.value.substring(end);

    // put caret at right position again
    this.selectionStart =
      this.selectionEnd = start + 4;
  }
})


// take data from code and input textareas,
// send POST reqeuest on server and place result from response
function request(event) {
  const str = document.querySelector('#code').value
  const inp = document.querySelector('#input').value
  let a = {code: str, input: inp}
  req.open("POST", "http://localhost:5000", true);
  req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  req.send(JSON.stringify(a));
}




