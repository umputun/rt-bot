package ru.hixon.controllers

import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestMethod
import org.springframework.web.bind.annotation.RestController
import ru.hixon.domain.InfoResponse
import ru.hixon.domain.VoteRequest
import ru.hixon.domain.VoteResponse
import java.util.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger

@RestController
class HelloSpringBootController {

    private val idGenerator: AtomicInteger = AtomicInteger(0)
    private val questions: ConcurrentHashMap<Int, String> = ConcurrentHashMap()
    private val resultAnswers: ConcurrentHashMap<Int, ConcurrentHashMap<String, AtomicInteger>> = ConcurrentHashMap()
    private val isVoted: ConcurrentHashMap<Int, ConcurrentHashMap<String, AtomicBoolean>> = ConcurrentHashMap()

    private enum class Command(val command: String) {
        START_VOTE("!голосование"),
        VOTE("!голосую"),
        VOTE_RESULT("!результат")
    }

    @RequestMapping(value = "/info", method = arrayOf(RequestMethod.GET))
    public fun info(): ResponseEntity<InfoResponse> {
        return ResponseEntity.ok(InfoResponse(commands = listOf<String>(
                "${Command.START_VOTE.command} Ваш вопрос? Вариант ответа 1, Вариант 2, Вариант 3",
                "${Command.VOTE.command} ID_голосования Вариант_ответа",
                "${Command.VOTE_RESULT.command} ID_голосования"
        )))
    }

    @RequestMapping(value = "/event", method = arrayOf(RequestMethod.POST))
    public fun event(@RequestBody voteRequest: VoteRequest): ResponseEntity<VoteResponse> {
        val cmd = voteRequest.textCommand.split(" ").first()

        if (cmd == Command.START_VOTE.command) {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(createVote(voteRequest))
        }

        if (cmd == Command.VOTE.command) {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(vote(voteRequest))
        }

        if (cmd == Command.VOTE_RESULT.command) {
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(voteResult(voteRequest))
        }

        return ResponseEntity.status(HttpStatus.EXPECTATION_FAILED).body(null);
    }

    private fun voteResult(voteRequest: VoteRequest): VoteResponse {
        val stringVoteId = voteRequest.textCommand.substring(Command.VOTE_RESULT.command.length + 1).trim()

        if (!stringVoteId.matches(Regex("\\d+"))) {
            return VoteResponse("Формат показа результатов: ${Command.VOTE_RESULT.command} ID_голосования")
        }

        val voteId = stringVoteId.toInt()
        val currentAnswers = resultAnswers.get(voteId)

        if (currentAnswers == null) {
            return VoteResponse("Голосования с таким ID не существует")
        }

        var totalCount: Double = 0.0
        currentAnswers.forEach { question, currentResult ->
            totalCount += currentResult.get()
        }

        val sj: StringJoiner = StringJoiner(", ", "Результат голосования с вопросом: ${questions.get(voteId)}: ", "")

        currentAnswers.forEach { question, currentResult ->
            var r = 0.0

            if (totalCount > 0.00001) {
                r = (100.0 * currentResult.get()) / totalCount
            }

            sj.add(" ${question} - ${r} (${currentResult.get()} голоса), ")
        }

        return VoteResponse(sj.toString())
    }

    private fun vote(voteRequest: VoteRequest): VoteResponse {
        val textCommand = voteRequest.textCommand.substring(Command.VOTE.command.length + 1).trim()

        if (!textCommand.contains(" ")) {
            return VoteResponse("Формат голосования: ${Command.VOTE.command} ID_голосования ваш_вариант")
        }

        val idAndAnswer = textCommand.split(" ")

        if (!idAndAnswer[0].trim().matches(Regex("\\d+"))) {
            return VoteResponse("Формат голосования: ${Command.VOTE.command} ID_голосования ваш_вариант")
        }

        val voteId = idAndAnswer[0].toInt()
        val currentQuestion = resultAnswers.get(voteId)

        if (currentQuestion == null) {
            return VoteResponse("Голосования с таким ID не существует")
        }

        var currentVoteMap = isVoted.get(voteId)
        if (currentVoteMap == null) {
            currentVoteMap = ConcurrentHashMap()
        } else {
            val userVote = currentVoteMap.get(voteRequest.userName)
            if (userVote != null) {
                return VoteResponse("Вы уже голосовали в голосовании с ID = $voteId")
            }
        }

        var isVote: Boolean = false

        currentQuestion.forEach { answer, currentVote ->
            if (answer == idAndAnswer[1]) {
                currentVote.getAndIncrement()
                isVote = true

                val voted: AtomicBoolean = AtomicBoolean(true)
                currentVoteMap!!.put(voteRequest.userName, voted)
                isVoted.put(voteId, currentVoteMap!!)
            }
        }

        if (!isVote) {
            return VoteResponse("В Голосовании с ID = ${idAndAnswer[0]} не существует варианта ответа = ${idAndAnswer[1]}")
        }

        return VoteResponse("${voteRequest.displayName} проголосовал за ${idAndAnswer[1]}")
    }

    private fun createVote(voteRequest: VoteRequest): VoteResponse {
        val textCommand = voteRequest.textCommand

        if (!textCommand.contains("?")) {
            return VoteResponse("Вопрос для голосования должен содержать знак вопроса - ?")
        }

        val splitByQuestion = textCommand.substring(Command.START_VOTE.command.length + 1).split("?")

        if (!splitByQuestion[1].contains(",")) {
            return VoteResponse("Варианты ответа для голосования должны быть разделены запятой - ,")
        }

        val question = splitByQuestion[0] + "?"
        val answers = splitByQuestion[1].split(",").map(String::trim)
        val id = idGenerator.incrementAndGet()

        questions.put(id, question)
        val ans : ConcurrentHashMap<String, AtomicInteger> = ConcurrentHashMap()

        answers.forEach {
            val vote : AtomicInteger = AtomicInteger(0)
            ans.put(it, vote)
        }

        resultAnswers.put(id, ans)

        return VoteResponse("Голосование создано. Id = $id , вопрос = $question, варианты ответа = $answers")
    }
}