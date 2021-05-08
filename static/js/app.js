let cart = {}

function create_new_element(material, quantity) {
  let element = document.createElement("div");
  element.classList.add("order-list-element");
  material_text = document.createTextNode(material);
  quantity_text = document.createTextNode(quantity + " hL");
  material_div = document.createElement("div");
  material_div.classList.add("order-list-material");
  material_div.appendChild(material_text);
  quantity_div = document.createElement("div");
  quantity_div.classList.add("order-list-quantity");
  quantity_div.appendChild(quantity_text);
  element.appendChild(material_div);
  element.appendChild(quantity_div);
  return element;
}

function add_to_cart(material, quantity) {
  let parent = document.getElementById("orders");
  parent.appendChild(create_new_element(material, quantity));
  cart[material] = quantity;
  console.log(cart)
}

function submitForm(event) {
  event.preventDefault();
  if (event.target.elements.material.value == "" || event.target.elements.quantity.value == "")
    return;
  add_to_cart(event.target.elements.material.value, event.target.elements.quantity.value);
}

function handleOrder(wholesaler, preds, material_pred_dict) {
  data = {
    "wholesaler": wholesaler,
    "cart": cart,
    "preds": preds,
    "material_pred_dict": material_pred_dict
  }
  fetch("/order", {
    method: "POST", 
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    },
  }).then(res => {
    console.log("Request complete! response:", res);
  });  
}
