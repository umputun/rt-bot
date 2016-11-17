package main

import (
	"errors"
)

var openingBrackets = [...]rune{'(', '[', '{', '<', '«'}
var closingBrackets = [...]rune{')', ']', '}', '>', '»'}

var inconsistentError = errors.New("Stack is inconsistent")
var emptyError = errors.New("Stack is empty")

type bracketsStack []rune

func (a *bracketsStack) pop() (rune, error) {
	var s rune
	if len(*a) < 1 {
		return s, emptyError
	} else {
		s = (*a)[len(*a)-1]
		*a = (*a)[:len(*a)-1]
		return s, nil
	}
}

func (a *bracketsStack) push(s rune) {
	*a = append(*a, s)
}

func (a *bracketsStack) processSymbol(s rune) error {
	for _, opening_bracket := range openingBrackets {
		if s == opening_bracket {
			a.push(s)
		}
	}
	for i, closing_bracket := range closingBrackets {
		if s == closing_bracket {
			opening_bracket, err := a.pop()
			if err != nil {
				return err
			}
			if opening_bracket != openingBrackets[i] {
				return inconsistentError
			}
		}
	}
	return nil
}

func (a bracketsStack) getResult() []rune {

	runes := []rune{}
	for {
		s, err := a.pop()
		if err != nil {
			break
		}
		for i, opening_bracket := range openingBrackets {
			if s == opening_bracket {
				runes = append(runes, closingBrackets[i])
			}
		}
	}
	return runes
}

func processString(str string) (string, error) {
	runes := []rune(str)
	brackets_stack := bracketsStack{}
	for _, s := range runes {
		err := brackets_stack.processSymbol(s)
		if err != nil {
			return "", err
		}
	}
	return string(brackets_stack.getResult()), nil
}
