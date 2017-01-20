import re, sys


def parse_profile_lines(lines):

  class ProfileChunk:
    def __init__(self):
      self.mem_increments = []
      self.mem_values = []
      self.lines = []

  READING_HEADER, READING_BODY, SKIPPING = 0, 1, 2

  state = SKIPPING
  chunks = []
  curr_chunk = None
  for line in lines:
    line = line.rstrip()

    if re.match('(GET|POST|PUT|DELETE) http://localhost[/a-z0-9]+', line):
      curr_chunk = ProfileChunk()
      chunks.append(curr_chunk)
      curr_chunk.lines.append(line)
    elif line == 'Line #    Mem usage    Increment   Line Contents':
      state = READING_HEADER
    elif state == READING_HEADER:
      state = READING_BODY
    elif state == READING_BODY:
      if not re.search('^ +[0-9]+', line):
        state = SKIPPING
      else:
        curr_chunk.lines.append(line)
        match = re.search(' +[0-9]+ +([0-9]+\.[0-9]+) MiB +([0-9]+\.[0-9]+) MiB', line)
        if match:
          curr_chunk.mem_values.append(float(match.group(1)))
          curr_chunk.mem_increments.append(float(match.group(2)))

  return chunks


if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[-1] == 'test':
    with open('test_output.txt') as f:
      text = f.read()
    lines = text.splitlines()
  else:
    lines = sys.stdin.read().splitlines()
  chunks = parse_profile_lines(lines)
  # for chunk in sorted(chunks, key=lambda chunk: -sum(chunk.mem_increments)):
  for chunk in chunks:
    if not chunk.mem_values:
      continue
    sum_inc = sum(chunk.mem_increments)
    print '{:<50} total inc: {:<5} end val: {:<5}'.format(
      chunk.lines[0][:50], sum_inc, chunk.mem_values[-1])
