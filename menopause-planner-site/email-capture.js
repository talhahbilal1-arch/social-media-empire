(function(){
  if(document.cookie.indexOf('mp_email_shown=1')!==-1)return;
  var bar=document.createElement('div');
  bar.className='email-capture-bar';
  bar.innerHTML='<div class="email-capture-inner">'+
    '<span class="ec-text">Free Menopause Symptom Tracker PDF</span>'+
    '<form class="ec-form" action="https://app.kit.com/forms/MENOPAUSE_FORM_ID/subscriptions" method="post">'+
      '<input type="email" name="email_address" placeholder="Your email" required>'+
      '<button type="submit" class="ec-btn">Download Free Tracker</button>'+
    '</form>'+
    '<button class="ec-close" aria-label="Close">&times;</button>'+
  '</div>';
  document.body.appendChild(bar);
  bar.querySelector('.ec-close').addEventListener('click',function(){
    bar.classList.remove('visible');
    document.cookie='mp_email_shown=1;path=/;max-age='+60*60*24*7;
  });
  setTimeout(function(){bar.classList.add('visible');},5000);
})();
