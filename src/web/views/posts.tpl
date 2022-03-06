{% extends 'index.tpl' %}
{% block postsblock %}
      <div class="album py-5 bg-light">
        <div class="container">
          <div class="row">
          {% for post in posts %}
            <div class="col-md-4">
              <div class="card mb-4 box-shadow">
                <div class="card-body">
                  <p class="card-text">{{ post.text }}</p>
                  <div class="d-flex justify-content-between align-items-center">
                    <!-- NOTE(ivasilev) Later make button conditional if admin token passed -->
                    <!-- <div class="btn&#45;group"> -->
                    <!--   <button type="button" class="btn btn&#45;sm btn&#45;outline&#45;secondary">Delete</button> -->
                    <!-- </div> -->
                    <small class="text-muted">{{ post.date }}</small>
                  </div>
                </div>
              </div>
            </div>
          {% endfor %}
          </div>
        </div>
      </div>
{% endblock %}
