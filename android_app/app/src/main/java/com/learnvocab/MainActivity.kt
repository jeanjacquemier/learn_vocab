package com.learnvocab

import android.content.Context
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.inputmethod.EditorInfo
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.util.*
import kotlin.collections.ArrayList

class MainActivity : AppCompatActivity() {
    private lateinit var fraText: TextView
    private lateinit var feedbackText: TextView
    private lateinit var input: EditText
    private lateinit var submitBtn: Button

    private var mapping: MutableMap<String, MutableList<String>> = mutableMapOf()
    private var keys: MutableList<String> = mutableListOf()
    private var pool: MutableList<String> = mutableListOf()
    private var scores: MutableMap<String, Int> = mutableMapOf()

    private val PREFS = "learn_vocab_prefs"
    private val POOL_KEY = "pool"
    private val SCORES_KEY = "scores"
    private val POOL_SIZE = 10

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        fraText = findViewById(R.id.fraText)
        feedbackText = findViewById(R.id.feedbackText)
        input = findViewById(R.id.input)
        submitBtn = findViewById(R.id.submitBtn)

        loadData()
        restoreState()

        showRandomPhrase()

        submitBtn.setOnClickListener {
            val user = input.text.toString().trim()
            if (user.isEmpty()) return@setOnClickListener
            val current = fraText.text.toString()
            val answers = mapping[current] ?: listOf()
            val correct = checkAnswer(user, answers)
            if (correct) {
                val newScore = (scores[current] ?: 0) + 1
                scores[current] = newScore
                feedbackText.text = "Correct! Score: $newScore/5"
                if (newScore >= 5) {
                    pool.remove(current)
                    addReplacement(current)
                }
            } else {
                scores[current] = 0
                feedbackText.text = "Incorrect. Expected: ${answers.joinToString(", ")}"
            }
            saveState()
            // show next phrase
            showNextPhrase(current)
            input.setText("")
        }

        input.setOnEditorActionListener { v, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                submitBtn.performClick()
                true
            } else false
        }
    }

    private fun loadData() {
        try {
            val reader = BufferedReader(InputStreamReader(assets.open("fra.txt"), "UTF-8"))
            reader.useLines { lines ->
                lines.forEach { raw ->
                    val line = raw.trim()
                    if (line.isEmpty()) return@forEach
                    val parts = line.split('\t')
                    if (parts.size < 2) return@forEach
                    val eng = parts[0].trim()
                    val fra = parts[1].trim()
                    if (eng.isEmpty() || fra.isEmpty()) return@forEach
                    val list = mapping.getOrPut(fra) { mutableListOf() }
                    if (!list.contains(eng)) list.add(eng)
                }
            }
        } catch (e: Exception) {
            // fallback sample
            mapping["Bonjour"] = mutableListOf("Hello")
            mapping["Au revoir"] = mutableListOf("Goodbye")
        }
        keys = ArrayList(mapping.keys)
        // initialize scores defaults
        for (k in keys) scores.putIfAbsent(k, 0)
    }

    private fun normalize(s: String): String {
        var t = s.trim()
        while (t.isNotEmpty() && Character.getType(t.last()).let { it == Character.OTHER_PUNCTUATION.toInt() || it == Character.DASH_PUNCTUATION.toInt() }.not()) {
            break
        }
        // simple casefold
        t = t.lowercase(Locale.getDefault())
        return t
    }

    private fun checkAnswer(user: String, answers: List<String>): Boolean {
        val u = normalize(user)
        answers.forEach { a ->
            if (u == normalize(a)) return true
        }
        return false
    }

    private fun restoreState() {
        val prefs = getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val poolJson = prefs.getString(POOL_KEY, null)
        val scoresJson = prefs.getString(SCORES_KEY, null)
        if (scoresJson != null) {
            try {
                val obj = JSONObject(scoresJson)
                obj.keys().forEach { k ->
                    scores[k] = obj.getInt(k)
                }
            } catch (_: Exception) {}
        }
        if (poolJson != null) {
            try {
                val arr = JSONArray(poolJson)
                for (i in 0 until arr.length()) {
                    val v = arr.getString(i)
                    if (mapping.containsKey(v)) pool.add(v)
                }
            } catch (_: Exception) {}
        }
        // fill pool
        val candidates = keys.filter { !pool.contains(it) }.sortedBy { scores[it] ?: 0 }
        val rnd = Random()
        while (pool.size < POOL_SIZE && candidates.isNotEmpty()) {
            pool.add(candidates.first())
        }
        if (pool.isEmpty()) pool.addAll(keys)
    }

    private fun saveState() {
        val prefs = getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val editor = prefs.edit()
        val arr = JSONArray()
        pool.forEach { arr.put(it) }
        val scoresObj = JSONObject()
        scores.forEach { (k, v) -> scoresObj.put(k, v) }
        editor.putString(POOL_KEY, arr.toString())
        editor.putString(SCORES_KEY, scoresObj.toString())
        editor.apply()
    }

    private fun addReplacement(removed: String) {
        val remaining = keys.filter { !pool.contains(it) && it != removed }.sortedBy { scores[it] ?: 0 }
        if (remaining.isNotEmpty()) pool.add(remaining.first())
    }

    private fun showRandomPhrase() {
        if (pool.isEmpty()) return
        val rnd = Random()
        fraText.text = pool[rnd.nextInt(pool.size)]
    }

    private fun showNextPhrase(previous: String) {
        if (pool.isEmpty()) {
            fraText.text = previous
            return
        }
        val candidates = if (pool.size > 1) pool.filter { it != previous } else pool
        val rnd = Random()
        fraText.text = candidates[rnd.nextInt(candidates.size)]
    }
}
