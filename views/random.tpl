<!DOCTYPE html>
<html lang="en">
   <head>
      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta name="description" content="">
      <meta name="author" content="">
      <title>{{title}}</title>
      <!-- Css -->
      <link href="static/css/bootstrap.css" rel="stylesheet">
      <link href="static/css/style.css" rel="stylesheet">
   </head>
   <body>
      <nav class="navbar navbar-default color-fill navbar-fixed-top">
         <div class="col-md-12">
            <div class="nav">
               <button class="btn-nav">
               <span class="icon-bar top"></span>
               <span class="icon-bar middle"></span>
               <span class="icon-bar bottom"></span>
               </button>
            </div>
            <a class="navbar-brand" href="index.html">
            <img class="logo" src="static/img/1.jpg" alt="logo">
            </a>
            <div class="nav-content hideNav hidden">
               <ul class="nav-list vcenter">
                  <li class="nav-item"><a class="item-anchor" href="/">EVENTS</a></li>
                  <li class="nav-item"><a class="item-anchor" href="/upcoming">UPCOMING</a></li>
               </ul>
            </div>
         </div>
      </nav>
      <section>
         <div class="container">
            <div class="row">
               <div class="col-md-12">
                  <h1>
                     BJJ events
                  </h1>
                  <h4><a href="mailto:zhzhussupovkz@gmail.com">zhzhussupovkz@gmail.com</a></h4>
               </div>
            </div>
            <div class="row margin-top-45">
            % for item in events: 
                <div class="col-md-12">
                    <img class="img-responsive margin-top-45" src={{item['img']}} alt={{item['name']}}>
                    <p><b>{{item['name']}}</b></p>
                    <p>{{item['date']}}</p>
                    <p>{{item['location']}}</p>
               </div>
            % end
            </div>
         </div>
         </div>
      </section>
      <!-- script -->
      <script src="static/js/jquery.js"></script>
      <script src="static/js/bootstrap.min.js"></script>
      <script src="static/js/modernizr.js"></script>
      <script src="static/js/script.js"></script>
   </body>
</html>