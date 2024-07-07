import tarantool

TARANTOOL_SCORE_SPACE = "scores"
TARANTOOL_INTERESTS_SPACE = "interests"

conn = tarantool.Connection(host="127.0.0.1", port=3302)  # type: ignore
# Create score
conn.eval(f"box.schema.space.create('{TARANTOOL_SCORE_SPACE}',"
          "{if_not_exists=true})")
conn.eval(
    f"box.space.{TARANTOOL_SCORE_SPACE}:format"
    "({ name = 'key', type = 'string' },"
    "{ name = 'score', type = 'double' },})"
)
conn.eval(f"""box.space.{TARANTOOL_SCORE_SPACE}:create_index('primary',"""
          """{ parts = { 'key' } })""")
# Create interests
conn.eval(f"box.schema.space.create('{TARANTOOL_INTERESTS_SPACE}',"
          "{if_not_exists=true})")

conn.eval(
    f"box.space.{TARANTOOL_INTERESTS_SPACE}:format"
    """({ { name = 'key', type = 'integer' },"""
    "{ name = 'interests', type = 'array' },})"
)

conn.eval(f"""box.space.{TARANTOOL_INTERESTS_SPACE}:create_index('primary',"""
          """{ parts = { 'key' } })""")

conn.eval(f"""box.space.{TARANTOOL_INTERESTS_SPACE}:"""
          """insert{1,{'cars','travel'}}""")
conn.eval(f"""box.space.{TARANTOOL_INTERESTS_SPACE}:"""
          """insert{2,{'pets','sport'}}""")
conn.eval(f"""box.space.{TARANTOOL_INTERESTS_SPACE}:"""
          """insert{3,{'geek','otus'}}""")

conn.close()
