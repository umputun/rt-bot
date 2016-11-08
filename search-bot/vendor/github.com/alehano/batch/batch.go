/*
Package batch runs multiple funcs asynchronously
You have to call Start() in the beginning and Close() in the end.
*/
package batch

import "sync"

type Batch struct {
	workers int
	jobChan chan func() error
	errFn   func(error)
	wg      *sync.WaitGroup
}

// New creates new Batch instance
func New(workers int, errCallback func(error)) *Batch {
	return &Batch{
		workers: workers,
		jobChan: make(chan func() error),
		errFn:   errCallback,
		wg:      new(sync.WaitGroup),
	}
}

func (b Batch) Start() {
	for i := 0; i < b.workers; i++ {
		go func() {
			for job := range b.jobChan {
				err := job()
				if err != nil {
					b.errFn(err)
				}
				b.wg.Done()
			}
		}()
	}
}

func (b Batch) Add(fn func() error) {
	b.wg.Add(1)
	b.jobChan <- fn
}

func (b Batch) Close() {
	b.wg.Wait()
	close(b.jobChan)
}
