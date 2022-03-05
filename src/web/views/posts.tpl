{% extends 'index.tpl' %}
{% block postsblock %}
      <div class="album py-5 bg-light">
        <div class="container">
          <div class="row">
          {% for post in posts %}
            <div class="col-md-4">
              <div class="card mb-4 box-shadow">
                <img class="card-img-top" data-src="holder.js/100px225?theme=thumb&bg=55595c&fg=eceeef&text=Thumbnail" alt="Card image cap">
                <div class="card-body">
                  <p class="card-text">{{ post.text }}</p>
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="btn-group">
                      <button type="button" class="btn btn-sm btn-outline-secondary">View</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary">Edit</button>
                    </div>
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
