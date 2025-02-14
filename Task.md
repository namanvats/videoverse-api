# REST APIs for Video Files

## Requirements

1. All API calls must be authenticated (assume static API tokens)
2. Allow users to upload videos with configurable limits of size and duration
   - **Maximum size:** e.g. `5 mb`, `25 mb`
   - **Minimum and maximum duration:** e.g. `25 secs`, `5 secs`
3. Allow trimming a video
   - For a given video clip (previously uploaded) shorten it from start or end
4. Allow merging video clips
   - For a given list of video clips (previously uploaded) stitch them into a single video file
5. Allow link sharing with time-based expiry (assume the expiry time)
6. Write unit and e2e tests. Add the command for test coverage.
7. Use SQLite as the database (commit it to the repo)
8. API Docs as `Swagger Endpoint` or `Postman Collection json`

## Expectations

- API Design Best Practices
- Documentation of any assumptions or choices made and why in `README.md`
- Links as citation to any article / code referred to or used
- Appropriate exception handling and error messages
- Code Quality - remove any unnecessary code, avoid large functions
