# batch
Package batch runs multiple funcs asynchronously

```go

    workers := 5
    
	batch := New(workers, func(err error) {
		log.Println(err.Error())
	})
	
	batch.Start()

	for i := 1; i <= 10; i++ {

		// Here we pass i parameter from outer scope
		fn := func(i int) func() error {
			return func() error {
				// Here is our job
			    err := SomeJob(i)
			    if err != nil {
			        return err
			    }
			    return nil
			}
			
		}
		batch.Add(fn(i))
	}
	batch.Close()

```