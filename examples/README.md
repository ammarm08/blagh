# Example Program

Inputs:

* `my-blog-post.blagh`
* `my-template.html`

Run:

```bash
blagh --file `my-blog-post.blagh` --template `my-template.html`
```

Output:

```bash
my-blog-post/
|-- index.html
```

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <title>My First Blog Post- Walt Whitman</title>
  </head>
  <body>
    <div class="main">
      <div class="conversation">
        <p> What do you think, ol' chap? </p>
      </div>
    </div>
    <footer>
      <div class="credits">
        <p> Fin </p>
      </div>
    </footer>
  </body>
</html>

```
