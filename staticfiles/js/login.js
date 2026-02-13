const container = document.getElementById('container');
const registerBtn = document.getElementById('registerBtn');
const LoginBtn = document.getElementById('LoginBtn');

registerBtn.addEventListener('click',() => {
    container.classList.add("active");
});
LoginBtn.addEventListener('click',() => {
    container.classList.remove("active");
});