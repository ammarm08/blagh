# Blagh

Blagh. I want my blog posts more straightforward to write. I am new to Python and wanted a good itch to scratch to improve my skillz.

The basic idea with `blagh` is this:
1. write a `.blagh` file. This contains all your variables.
2. write a template `.html` file. All your variables get injected here.

See below for the specifics of all this.

# Table of Contents

1. [ Usage ](#usage)
2. [ Writing Templates ](#writing-templates)
3. [ Writing Blagh Files ](#writing-blagh-files)
4. [ Sample Output ](#sample-output)
5. [ TODO: Importing Blagh Files ](#importing-blagh-files)


# Usage

```bash
blagh --file your-blog-post.blagh --template your-template.html
```

This will produce a folder with your blog post's filename and an index.html
with your compiled html.


# Writing Templates

Template HTML looks like this:

```
<html>
  <head>
    // ... some head stuff like stylesheets and what not
    <title> $slug$ </title>
  </head>
  <body>
    <div class="main">
      $content$
    </div>
    <div class="footer">
      $footer$
    </div>
  </body>
</html>
```

Pretty straightforward. Make it valid HTML. Throw in `$name-of-variable$`
for areas you want to inject data into. The way that they are used will be discussed below.


# Writing Blagh Files

Blagh files look like this:

```
// TODO: implement imports
<imports>
</imports>

<globals>
  $slug$ := my-awesome-blog-post
</globals>

<variables>
  $title$ := My Awesome Blog Post
</variables>

<macros>
  $conversation$ := <div class="conversation">{}</div>
</macros>

<content>
  <h3> $title$ </h3>

  This is a conversation:

  <conversation>
    Hi how are you?
  </conversation>
</content>

<footer>
  Good bye
</footer>
```

## Globals

These are accessible *only* in the template HTML file.

## Variables

These are accessible *only* in custom content tags (ie, tags that aren't globals, variables, or macros)

## Macros

These are dollar-sign-couched keywords that help you create custom HTML elements and inject them within your custom content block. They require a `{}` to signal where the data should be injected.

## Imports

TODO: This is not implemented yet.

You can import globals, variables, and macros from another `.blagh` file. See the "Importing Blagh Files" section for more.


## Custom Content Tags

This is what gets compiled by `blagh` and injected into your template HTML's `$content$` or `$footer` or `$name-your-tag$` areas.

You can name these tags whatever you want. You can create tags in your `.blagh` file by simply doing the following:

```
<a-tag>
</a-tag>
```


# Sample Output

The above sample `.blagh` and template `.html` files will produce the following HTML:

```
<html>
  <head>
    <title> my-awesome-blog-post </title>
  </head>
  <body>
    <div class="main">
      <h3> My Awesome Blog Post </h3>
      <p> This is a conversation: </p>
      <div class="conversation">
        <p> Hi, how are you? </p>
      </div>
    </div>
    <div class="footer">
      <p> Good bye </p>
    </div>
  </body>
</html>
```

This will exist in `my-awesome-blog-post/index.html`.


# TODO: Importing Blagh Files

Not implemented yet!

As mentioned above, you can also *import* `.blagh` files into other `.blagh` files. The globals, variables, and macros defined in one will now be available to the file that imported it.

This is very useful because if your blog makes repeated use of certain variables or HTML macros, you just need to create one `.blagh` file and import it when writing your blog posts.

Note: *only* the `<macros>`, `<globals>`, and `<variables>` tags are ever imported.

So let's rewrite the above example to take advantage of imports.


`variables.blagh`:
```
<globals>
  $slug$ := my-awesome-blog-post
</globals>

<variables>
  $title$ := My Awesome Blog Post
</variables>

<macros>
  $conversation$ := <div class="conversation">{}</div>
</macros>
```

`my-blog-post.blagh`:
```
<imports>
  $variables$
</imports>

<content>
  <h3> $title$ </h3>

  This is a conversation:

  <conversation>
    Hi how are you?
  </conversation>
</content>

<footer>
  Good bye
</footer>
```

You can import multiple files! For instance, you could break up your macros into a file called `macros.blagh` and your globals into a `globals.blagh`, and then import them in your blog post file as such:

```
<imports>
  $macros$
  $globals$
</imports>
```

These will be imported in the order they are listed. Name conflicts will result in a compile error. Names are scoped to block type. You cannot have name reassignment.
