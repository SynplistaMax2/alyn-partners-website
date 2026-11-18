(function(){
  var menuBtn=document.getElementById('menu-btn'),mobile=document.getElementById('mobile-nav');
  var ddBtn=document.getElementById('dd-btn'),dd=ddBtn.parentElement;
  menuBtn.addEventListener('click',function(){var o=mobile.classList.toggle('open');menuBtn.setAttribute('aria-expanded',o?'true':'false')});
  ddBtn.addEventListener('click',function(){var o=dd.classList.toggle('open');ddBtn.setAttribute('aria-expanded',o?'true':'false')});
  document.addEventListener('click',function(e){if(!dd.contains(e.target)){dd.classList.remove('open');ddBtn.setAttribute('aria-expanded','false')}});
  mobile.addEventListener('click',function(e){if(e.target.closest('a')){mobile.classList.remove('open');menuBtn.setAttribute('aria-expanded','false')}});
  var top=document.querySelector('.to-top');
  if(top){top.addEventListener('click',function(e){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'})})}
})();
