// have imgs in array
const focusIMG = document.querySelector('#slide-focus')
const content = document.querySelector('#slide-content')
let idx = 0;
function init() {
  content.innerHTML = ''
  for (let [i,img] of images.entries()) {
    content.innerHTML+=`
    <img src='${img}' onclick='update(${i})' class='slide-img'>
    `
  }
  update(0)
}
function update(i) {
  focusIMG.innerHTML = `<img src="${images[i]}">`
  try {
    document.querySelector('.slide-img.focussed-img').classList.remove('focussed-img')
  } catch (error) {
    
  }
  document.querySelectorAll('.slide-img')[i].classList.add('focussed-img')
  content.style.left = (-i*180+180)+'px';
  idx = i
}
function left() {
  idx = Math.max(idx-1,0)
  update(idx)
}
function right() {
  idx = Math.min(idx+1,document.querySelectorAll('.slide-img').length-1)
  update(idx)
}