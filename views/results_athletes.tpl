<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="BJJ events">
    <meta name="generator" content="Jekyll v3.8.5">
    <title>{{title}}</title>

    <!-- Bootstrap core CSS -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/flags.min.css" rel="stylesheet">
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
    <link href="/static/css/cover.css" rel="stylesheet">
  </head>

  <body class="d-flex flex-column h-100">
  <header>
    <!-- Fixed navbar -->
    <nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
      <a class="navbar-brand" href="/">{{header}}</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarCollapse">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">Upcoming</a>
            <div class="dropdown-menu" x-placement="bottom-start" style="position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(0px, 40px, 0px);">
              <a class="dropdown-item" href="/">Smoothcomp</a>
              <a class="dropdown-item" href="/upcoming/uaejjf">UAEJJF</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="/upcoming/all">ALL</a>
            </div>
          </li>
          <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">Results</a>
                <div class="dropdown-menu" x-placement="bottom-start" style="position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(0px, 40px, 0px);">
                % if menu == "uaejjf":
                      <a class="dropdown-item active" href="/kazakhstan_results/uaejjf">UAEJJF<span class="sr-only">(current)</span></a>
                      <a class="dropdown-item" href="/kazakhstan_results/smoothcomp">Smoothcomp</a>
                % else:
                    <a class="dropdown-item" href="/kazakhstan_results/uaejjf">UAEJJF</a>
                    <a class="dropdown-item active" href="/kazakhstan_results/smoothcomp">Smoothcomp<span class="sr-only">(current)</span></a>                       
                % end
                </div>
            </li>
          %if user:
            <li class="nav-item">
              <a class="nav-link" href="/logout">Logout</a>
            </li>
          %end
        </ul>
        <form class="form-inline mt-2 mt-md-0">
          <input class="form-control mr-sm-2" type="text" placeholder="Search" aria-label="Search">
          <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
        </form>
      </div>
    </nav>
  </header>

  <main role="main" class="flex-shrink-0">
    <div class="container">
      <div class="row">
        <h1>{{event}}</h1>
      </div>
      <div class="row">
        <ul class="list-group">
            <li class="list-group-item d-flex">
                <img src="/static/img/1_place.png" alt="total gold" /> {{gold}}
            </li>
            <li class="list-group-item d-flex">
                <img src="/static/img/2_place.png" alt="total silver" /> {{silver}}
            </li>
            <li class="list-group-item d-flex">
                <img src="/static/img/3_place.png" alt="total bronze" /> {{bronze}}
            </li>
        </ul>
      </div>

      <div class="row">
        <table class="table table-hover">
        <thead>
          <tr>
            <th scope="col">ATHLETE COUNTRY</th>
            <td scope="col">TEAM</td>
            <td scope="col">DIVISION</td>
            <td scope="col">PLACE</td>
          </tr>
        </thead>
        <tbody>
        % for a in athletes:
            <tr>
                % if a['profile_id']:
                    % if menu == "uaejjf":
                        <td>{{a['name']}} <a href = "/uaejjf/profile/{{a['profile_id']}}"> info </a></td>
                    % else:
                        <td>{{a['name']}} <a href = "/smoothcomp/profile/{{a['profile_id']}}"> info </a></td>
                    % end                        
                % else:
                    <td>{{a['name']}}</td>
                % end
                <td>{{a['team']}}</td>
                <td>{{a['division']}}</td>
                <td><img src="/static/img/{{a['place']}}_place.png" alt={{a['place']}} /></td>
            </tr>
        % end
        <tr><td colspan="4"><center>Last update: {{last_update}}</center></td></tr>
        </tbody>
        </table>
      </div>
    </div>
  </main>

  <footer class="mt-auto">
    <div class="container">
      <p>BJJ events by <a href="mailto:zhzhussupovkz@gmail.com">@zhzhussupovkz</a></p>
    </div>
  </footer>
</body>
</html>

