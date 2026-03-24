(function(){
  if(document.cookie.indexOf('ddd_email_shown=1')!==-1)return;
  var bar=document.createElement('div');
  bar.className='email-capture-bar';
  bar.innerHTML='<div class="email-capture-inner">'+
    '<span class="ec-text">Get the Top 10 Deals Every Monday &mdash; Free</span>'+
    '<form class="ec-form" action="https://app.kit.com/forms/DDD_FORM_ID/subscriptions" method="post">'+
      '<input type="email" name="email_address" placeholder="Your email" required>'+
      '<button type="submit" class="ec-btn">Send Me the Deals</button>'+
    '</form>'+
    '<button class="ec-close" aria-label="Close">&times;</button>'+
  '</div>';
  document.body.appendChild(bar);
  bar.querySelector('.ec-close').addEventListener('click',function(){
    bar.classList.remove('visible');
    document.cookie='ddd_email_shown=1;path=/;max-age='+60*60*24*7;
  });
  setTimeout(function(){bar.classList.add('visible');},5000);
})();
