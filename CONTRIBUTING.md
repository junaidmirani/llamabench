# Contributing to llamabench

Thanks for your interest in contributing! llamabench is an early-stage MVP and there's lots of room for improvement.

## How to Contribute

### Reporting Issues
- Check existing issues first
- Include system info (OS, Python version, GPU)
- Provide benchmark results if relevant
- Share error messages and stack traces

### Suggesting Features
- Open an issue with the `enhancement` label
- Describe the use case clearly
- Explain why it would be valuable
- Consider implementation complexity

### Pull Requests

#### Setup Development Environment
```bash
git clone https://github.com/yourusername/llamabench.git
cd llamabench
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Before Submitting
- [ ] Test your changes locally
- [ ] Add docstrings for new functions
- [ ] Update README if adding features
- [ ] Keep changes focused and atomic

#### PR Guidelines
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Priority Areas

### High Priority
- **Real HTTP load testing**: Replace mock data with actual requests
- **Docker automation**: Auto-pull and start containers
- **More models**: Add Gemma, Phi-3, CodeLlama
- **Quantization support**: Test Q4, Q5, Q8 variants
- **GPU metrics**: Track utilization, memory bandwidth

### Medium Priority
- **Windows/Mac testing**: Ensure cross-platform compatibility
- **Web UI**: Visualize results in browser
- **CI/CD integration**: GitHub Actions for regression testing
- **Better error handling**: Graceful failures
- **Progress bars**: Show benchmark progress

### Nice to Have
- **Custom model support**: User-provided HuggingFace repos
- **Distributed benchmarks**: Multi-GPU, multi-node
- **Historical tracking**: Compare results over time
- **Cost optimization**: Recommend cheapest cloud instance
- **Slack/Discord notifications**: Alert when benchmarks complete

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and small
- Add comments for complex logic
- Use meaningful variable names

## Testing

Right now we don't have a formal test suite. If you're adding critical functionality, consider adding basic tests:

```python
def test_benchmark_result_parsing():
    result = parse_benchmark_result(sample_data)
    assert result['throughput'] > 0
    assert result['ttft'] > 0
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Include usage examples in docstrings

## Community

- Be respectful and constructive
- Help others in issues and discussions
- Share your benchmark results!
- Blog about llamabench and share the link

## Questions?

Open an issue with the `question` label or start a discussion.

---

llamabench is MIT licensed. By contributing, you agree your contributions will be licensed under the same license.
