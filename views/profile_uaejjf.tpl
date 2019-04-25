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
          <!-- <li class="nav-item">
            <a class="nav-link" href="/random">Random</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/all">All</a>
          </li> -->
          <li class="nav-item active">
            <a class="nav-link" href="/kazakhstan_results">Results<span class="sr-only">(current)</span></a>
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
        <div class="card mb-6">
            <div class="card-body">
              <h5 class="card-title">{{profile['name']}}</h5>
            </div>
            <center><img style="width: 128px;" src="data:image/png;base64, {{profile['img']}}" alt={{profile['name']}}></center>
            <ul class="list-group list-group-flush">
            % for k, v in profile['info'].items():
                <li class="list-group-item">{{k}} - {{v}}</li>
            % end
            </ul>
        </div>
      </div>
          
    % for event in profile['event_matches']:
        <div class="row">
        <table class="table table-hover">
        <thead>
          <tr>
            <th scope="col">Result</th>
            <td scope="col">Competitor</td>
            <td scope="col">Division</td>
            <td scope="col">Event</td>
            <td scope="col">Event Date</td>
          </tr>
        </thead>
        <tbody>
        % for match in event['matches']:
            <tr>
                <td>{{match['result']}}</td>
                <td>{{match['competitor']}}</td>
                <td>{{match['division']}}</td>
                <td>{{event['event']['name']}}</td>
                <td>
                % for d in event['event']['date']:
                    {{d}}<br>
                % end
                </td>
            </tr>
        % end
        <tr><td colspan = "5"><center>PLACEMENT {{event['place']}}</td></center></tr>
        </tbody>
        </table>
        </div>
        <br/>
    % end

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

