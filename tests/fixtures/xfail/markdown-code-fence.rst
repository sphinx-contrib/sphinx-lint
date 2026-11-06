.. expect: markdown code fence found, rst uses a literal block ("::") or a "code-block" directive (markdown-code-fence)

Sphinx silently renders the following as text instead of a code block:

```python
print("hello")
```

That's bad.
