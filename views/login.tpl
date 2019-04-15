<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="BJJ events">
    <meta name="generator" content="Jekyll v3.8.5">
    <title>{{title}}</title>

    <link href="static/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

    <style>
      .bd-placeholder-img {
        font-size: 1.125rem;
        text-anchor: middle;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
      }

      @media (min-width: 768px) {
        .bd-placeholder-img-lg {
          font-size: 3.5rem;
        }
      }
    </style>
    <!-- Custom styles for this template -->
    <link href="static/css/signin.css" rel="stylesheet">
  </head>
  <body class="text-center">
    <form action method="post" class="form-signin" id="login_form">
  <img class="mb-4" src="static/img/login.png" alt="" width="72" height="72">
  <legend>Log in</legend>
  <div class="form-group">
      <label for="inputEmail" class="sr-only">Email address</label>
      <input type="email" name="email" id="inputEmail" class="form-control" placeholder="Email address" required autofocus>
  </div>
  <div class="form-group">
      <label for="inputPassword" class="sr-only">Password</label>
      <input type="password" name="password" id="inputPassword" class="form-control" placeholder="Password" required>
  </div>      
  <button class="btn btn-lg btn-primary btn-block" type="submit">Go!</button>
  <p class="mt-5 mb-3 text-muted">&copy; bjj events</p>
</form>

    <script type="text/javascript">
        $(document).ready(function($) {
            $("#login_form").submit(function(e) {
                $('#submit').prop('disabled', true);
             });
        });
    </script>
</body>
</html>
