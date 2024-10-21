

function createDefaultActionForm(parentElement, route, buttonTitle, buttonIcon, buttonClass, method="POST"){
  var form = document.createElement("form");
  form.className = "actionForm";
  form.action = route;
  form.method = method;
  parentElement.appendChild(form);
  var button = document.createElement("button");
  button.type = "submit";
  button.className = buttonClass;
  button.title = buttonTitle;
  // Check if buttonIcon is an array
  if (!Array.isArray(buttonIcon)){
    buttonIcon = [buttonIcon];  // Convert to array, so that it wont be read as string
  }
  for (var i = 0; i < buttonIcon.length; i++){
    button.innerHTML += "<ion-icon name='" + buttonIcon[i] + "'></ion-icon>";
  }
  form.appendChild(button);
  return [form, button];
}

function createHiddenFormInput(form, name, value){
    var input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.value = value;
    form.appendChild(input);
    return input;
}

function createHintElement(hintParagraph, hintText){
    hintParagraph.title = hintText;
    hintParagraph.style.cursor = "help";
    var icon = document.createElement("ion-icon");
    icon.style.color = "grey";
    icon.name = "information-circle";
    hintParagraph.appendChild(icon);
}