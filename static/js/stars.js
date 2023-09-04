const s1 = $('#star1')[0];
const s2 = $('#star2')[0];
const s3 = $('#star3')[0];
const s4 = $('#star4')[0];
const s5 = $('#star5')[0];
const s = [s1,s2,s3,s4,s5];
var stars = 0;
function initStars() {
    for (let i of s) {
        i.addEventListener('mouseover',()=>{
            addStars(parseInt(i.id[4]))
        });
        i.addEventListener('mouseout',()=>{
            removeStars(5)
        });
        i.addEventListener('click',()=>{
            stars=parseInt(i.id[4]);
            document.querySelector('#star_i').value = stars
            addStars(stars)
        })
    }
}


function addStars(n) {
    removeStars(5,false)
    for (let i of s.slice(0,n)) {
        i.classList.add('star-select');
    }
}
function removeStars(n,rs = true) {
    for (let i of s.slice(0,n)) {
        i.classList.remove('star-select');
    }
    if (rs) {
        addStars(stars)
    }
}
function getStars() {
    let r = 0;
    for (let i of s) {
        if (i.classList.contains('star-select')) {
            r+=1;
        }
    }
    return r;
}