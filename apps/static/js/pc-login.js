/*huanglin*/
function login_check(){
  uuid=$("#loginqrcode").attr("name");
  geturl="/sso/authorize";

  $.ajax({
    cache: false,
    type: "GET",
    url: geturl,
    async: false,

    error: function(request){
      window.location = "/pc_login_fail.html";
    },

    success: function(data){
      var responsedata=jQuery.parseJSON(data);
      authflag=responsedata.authorized;
      //alert(authflag)
      if(authflag==true)
      {
        nexturl=responsedata.redirect_uri;
        //alert(nexturl)
        window.location = nexturl;
        return
      }
      else if (authflag==-1)
      {
        window.location = "/pc_login_fail.html";
      }
      setTimeout(login_check,3000)
    }
  });

  return
}

function login_clear(){
  uuid=$("#loginqrcode").attr("name");
  posturl="/sso/login_delete";

  var data = {
      data: JSON.stringify({
                "uuid":uuid,
              })
    }

  $.ajax({
    cache: false,
    type: "POST",
    url: posturl,
    data: data,
    async: false,

    error: function(request){
    },

    success: function(data){
    }
  });

  return
}

window.onload=function(){
  login_check();
}

window.onbeforeunload=function(){
  login_clear();
}


