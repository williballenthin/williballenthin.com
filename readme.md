## new post

```console
hugo new content/posts/(date +%Y-%m-%d)-idapython-virtualenv.md
```

## prepare

```console
npm install
```


## build

```console
hugo
npx rehype-cli public -o
```


## serve (debug)

```console
hugo serve
# -or-
python -m http.server --bind localhost --directory public/
```
