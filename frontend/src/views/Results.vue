<template>
  <div class="min-h-screen bg-gray-900 text-white py-10">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-2xl font-bold text-green-400 mb-8 text-center">
        检测结果
      </h1>

      <div v-if="loading" class="text-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto"></div>
        <p class="mt-4 text-gray-400">加载中…</p>
      </div>

      <template v-else-if="result">
        <!-- 圆环 + 摘要 -->
        <div class="grid gap-6 md:grid-cols-2 md:items-stretch">
          <div
            class="bg-gray-800/80 rounded-xl border border-gray-700 p-4 flex flex-col items-center justify-center min-h-[280px]"
          >
            <p class="text-xs text-gray-500 mb-2 w-full text-center">
              {{ voteCaption }}
            </p>
            <div ref="donutChartEl" class="w-full h-[220px]"></div>
          </div>

          <div
            class="bg-gray-800/80 rounded-xl border border-gray-700 p-6 flex flex-col justify-center"
          >
            <h2 class="text-lg font-semibold text-green-400 mb-4">摘要</h2>
            <dl class="space-y-3 text-sm">
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">检测类型</dt>
                <dd class="text-gray-200 text-right">{{ kindLabel }}</dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">综合判定</dt>
                <dd :class="verdictClass" class="text-right font-semibold">
                  {{ verdictText }}
                </dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">{{ subjectLabel }}</dt>
                <dd class="text-gray-200 text-right break-all">{{ result.filename }}</dd>
              </div>
              <div class="flex justify-between gap-4 border-b border-gray-700 pb-2">
                <dt class="text-gray-500 shrink-0">状态</dt>
                <dd :class="getStatusColor(result.status)" class="text-right">
                  {{ getStatusText(result.status) }}
                </dd>
              </div>
              <div class="flex justify-between gap-4">
                <dt class="text-gray-500 shrink-0">检测时间</dt>
                <dd class="text-gray-200 text-right">{{ formatDate(result.created_at) }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- 切换 -->
        <div class="mt-8 flex rounded-lg overflow-hidden border border-gray-700 bg-gray-800/50">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="flex-1 py-3 px-2 text-sm font-medium transition sm:text-base"
            :class="
              activePanel === tab.key
                ? 'bg-green-600/20 text-green-400 border-b-2 border-green-500'
                : 'text-gray-400 hover:text-gray-200 border-b-2 border-transparent'
            "
            @click="activePanel = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 面板内容 -->
        <div class="mt-4 rounded-xl border border-gray-700 bg-gray-800/60 p-6 min-h-[240px]">
          <!-- 检测结果 -->
          <div v-show="activePanel === 'result'" class="space-y-6">
            <div v-if="resultKind === 'url'" class="space-y-4">
              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">URL 检测摘要</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">检测 URL</span>
                    <span class="text-gray-200 break-all text-right">{{ result.filename }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">提供方</span>
                    <span class="text-gray-200">{{ urlEnvelope?.provider || 'URLhaus' }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">查询状态</span>
                    <span class="text-gray-200">{{ urlQueryStatus }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">URL 状态</span>
                    <span class="text-gray-200">{{ urlStatus }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">恶意判定</span>
                    <span :class="verdictClass" class="font-semibold">{{ verdictText }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">黑名单标记</span>
                    <span class="text-gray-200">{{ urlThreatLevel }}</span>
                  </div>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">URLhaus 详细字段</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">记录 ID</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.id) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">主机</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.host) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">威胁类型</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.threat) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">上报者</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.reporter) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">首次入库</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.date_added) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">最近在线</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.last_online) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">是否下架（larted）</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.larted) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">下架耗时（秒）</span>
                    <span class="text-gray-200">{{ displayOrNull(urlRaw?.takedown_time_seconds) }}</span>
                  </div>
                </div>
                <a
                  v-if="urlRaw?.urlhaus_reference"
                  :href="urlRaw.urlhaus_reference"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block mt-3 text-green-400 hover:text-green-300 text-sm"
                >
                  打开 URLhaus 参考页 →
                </a>
              </div>

              <div v-if="urlBlacklistEntries.length" class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">黑名单明细</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div
                    v-for="entry in urlBlacklistEntries"
                    :key="entry.name"
                    class="flex justify-between gap-3 border-b border-gray-700 pb-2"
                  >
                    <span class="text-gray-500">{{ entry.name }}</span>
                    <span class="text-gray-200">{{ displayOrNull(entry.value) }}</span>
                  </div>
                </div>
              </div>

              <div v-if="urlTags.length" class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">标签</h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in urlTags"
                    :key="tag"
                    class="px-2 py-1 rounded bg-green-900/40 border border-green-700 text-green-300 text-xs"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">Payload 明细</h3>
                <div v-if="urlPayloads.length" class="space-y-3">
                  <div
                    v-for="(payload, idx) in urlPayloads"
                    :key="`${payload.response_sha256 || payload.response_md5 || idx}`"
                    class="rounded-lg border border-gray-700 bg-gray-950/60 p-3"
                  >
                    <div class="text-xs text-gray-500 mb-2">Payload #{{ idx + 1 }}</div>
                    <div class="grid sm:grid-cols-2 gap-2 text-sm">
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">firstseen</span>
                        <span class="text-gray-200">{{ displayOrNull(payload.firstseen) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">file_type</span>
                        <span class="text-gray-200">{{ displayOrNull(payload.file_type) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">filename</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.filename) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">response_size</span>
                        <span class="text-gray-200">{{ displayOrNull(payload.response_size) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">response_md5</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.response_md5) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">response_sha256</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.response_sha256) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">signature</span>
                        <span class="text-gray-200">{{ displayOrNull(payload.signature) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">virustotal</span>
                        <span class="text-gray-200">{{ displayOrNull(payload.virustotal) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">imphash</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.imphash) }}</span>
                      </div>
                      <div class="flex justify-between gap-3">
                        <span class="text-gray-500">ssdeep</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.ssdeep) }}</span>
                      </div>
                      <div class="flex justify-between gap-3 sm:col-span-2">
                        <span class="text-gray-500">tlsh</span>
                        <span class="text-gray-200 break-all">{{ displayOrNull(payload.tlsh) }}</span>
                      </div>
                    </div>
                    <a
                      v-if="payload.urlhaus_download"
                      :href="payload.urlhaus_download"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="inline-block mt-2 text-green-400 hover:text-green-300 text-xs"
                    >
                      下载样本（URLhaus） →
                    </a>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-500">无 payload 记录（NULL）</p>
              </div>
            </div>
            <div v-else-if="resultKind === 'hash'" class="space-y-4">
              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">哈希检测摘要</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">哈希值</span>
                    <span class="text-gray-200 break-all">{{ result.filename }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">提供方</span>
                    <span class="text-gray-200">{{ hashEnvelope?.provider || 'VirusTotal' }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">恶意引擎数</span>
                    <span class="text-gray-200">{{ displayOrNull(hashMalicious) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">总引擎数</span>
                    <span class="text-gray-200">{{ displayOrNull(hashTotalEngines) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">检测时间</span>
                    <span class="text-gray-200">{{ displayOrNull(hashLastAnalysisDate) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">类型标签</span>
                    <span class="text-gray-200">{{ displayOrNull(hashTypeTag) }}</span>
                  </div>
                </div>
              </div>

              <div v-if="hashTags.length" class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">标签</h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in hashTags"
                    :key="tag"
                    class="px-2 py-1 rounded bg-green-900/40 border border-green-700 text-green-300 text-xs"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">样本标识信息</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">data.id</span>
                    <span class="text-gray-200 break-all">{{ displayOrNull(hashData?.id) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">data.type</span>
                    <span class="text-gray-200">{{ displayOrNull(hashData?.type) }}</span>
                  </div>
                </div>
                <a
                  v-if="hashData?.links?.self"
                  :href="hashData.links.self"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block mt-3 text-green-400 hover:text-green-300 text-sm"
                >
                  打开 VT 资源链接 →
                </a>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">基础指纹</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">md5</span>
                    <span class="text-gray-200 break-all">{{ displayOrNull(hashAttr?.md5) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">sha1</span>
                    <span class="text-gray-200 break-all">{{ displayOrNull(hashAttr?.sha1) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">sha256</span>
                    <span class="text-gray-200 break-all">{{ displayOrNull(hashAttr?.sha256) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">size</span>
                    <span class="text-gray-200">{{ displayOrNull(hashAttr?.size) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">magic</span>
                    <span class="text-gray-200 break-all text-right">{{ displayOrNull(hashAttr?.magic) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">type_tag</span>
                    <span class="text-gray-200">{{ displayOrNull(hashAttr?.type_tag) }}</span>
                  </div>
                </div>
                <div v-if="hashNames.length" class="mt-3 text-sm">
                  <div class="text-gray-500 mb-1">names</div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="name in hashNames"
                      :key="name"
                      class="px-2 py-1 rounded bg-gray-800 border border-gray-700 text-gray-200 text-xs"
                    >
                      {{ name }}
                    </span>
                  </div>
                </div>
              </div>

              <div v-if="hashElfInfo" class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">静态结构信息（ELF）</h3>
                <div class="grid sm:grid-cols-3 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">machine</span>
                    <span class="text-gray-200">{{ displayOrNull(hashElfInfo?.header?.machine) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">class</span>
                    <span class="text-gray-200">{{ displayOrNull(hashElfInfo?.header?.class) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">type</span>
                    <span class="text-gray-200">{{ displayOrNull(hashElfInfo?.header?.type) }}</span>
                  </div>
                </div>
                <div class="mt-3 text-xs text-gray-500">
                  节区数：{{ hashSectionCount }}，段数：{{ hashSegmentCount }}
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">多引擎统计（last_analysis_stats）</h3>
                <div class="grid sm:grid-cols-4 gap-3 text-sm">
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500">malicious</div>
                    <div class="text-red-400 text-lg font-semibold">{{ displayOrNull(hashStats?.malicious) }}</div>
                  </div>
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500">suspicious</div>
                    <div class="text-yellow-400 text-lg font-semibold">{{ displayOrNull(hashStats?.suspicious) }}</div>
                  </div>
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500">undetected</div>
                    <div class="text-gray-200 text-lg font-semibold">{{ displayOrNull(hashStats?.undetected) }}</div>
                  </div>
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500">total</div>
                    <div class="text-green-400 text-lg font-semibold">{{ displayOrNull(hashTotalEngines) }}</div>
                  </div>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">提交与传播信息</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">times_submitted</span>
                    <span class="text-gray-200">{{ displayOrNull(hashAttr?.times_submitted) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">unique_sources</span>
                    <span class="text-gray-200">{{ displayOrNull(hashAttr?.unique_sources) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">first_seen_itw_date</span>
                    <span class="text-gray-200">{{ displayOrNull(formatUnixTs(hashAttr?.first_seen_itw_date)) }}</span>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">last_submission_date</span>
                    <span class="text-gray-200">{{ displayOrNull(formatUnixTs(hashAttr?.last_submission_date)) }}</span>
                  </div>
                </div>
              </div>

              <div v-if="hashThreatLabel" class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">威胁归类</h3>
                <div class="text-sm">
                  <div class="flex justify-between gap-3 border-b border-gray-700 pb-2">
                    <span class="text-gray-500">suggested_threat_label</span>
                    <span class="text-red-300 font-semibold">{{ hashThreatLabel }}</span>
                  </div>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">各引擎明细（last_analysis_results）</h3>
                <div class="max-h-80 overflow-y-auto rounded border border-gray-700">
                  <table class="min-w-full text-xs">
                    <thead class="bg-gray-950/70">
                      <tr>
                        <th class="px-3 py-2 text-left text-gray-400">Engine</th>
                        <th class="px-3 py-2 text-left text-gray-400">Category</th>
                        <th class="px-3 py-2 text-left text-gray-400">Result</th>
                        <th class="px-3 py-2 text-left text-gray-400">Version</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="e in hashEngineEntries"
                        :key="e.name"
                        class="border-t border-gray-800"
                      >
                        <td class="px-3 py-2 text-gray-200">{{ e.name }}</td>
                        <td class="px-3 py-2" :class="engineCategoryClass(e.category)">{{ displayOrNull(e.category) }}</td>
                        <td class="px-3 py-2 text-gray-300 break-all">{{ displayOrNull(e.result) }}</td>
                        <td class="px-3 py-2 text-gray-400">{{ displayOrNull(e.version) }}</td>
                      </tr>
                      <tr v-if="!hashEngineEntries.length">
                        <td colspan="4" class="px-3 py-3 text-center text-gray-500">NULL</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="bg-gray-900/60 rounded-lg p-4 border border-gray-700">
                <h3 class="text-sm font-semibold text-green-400 mb-3">社区/情报增强</h3>
                <div class="grid sm:grid-cols-2 gap-3 text-sm">
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500 mb-1">crowdsourced_ai_results</div>
                    <div class="text-gray-200">{{ hashAiCount }} 条</div>
                  </div>
                  <div class="bg-gray-950/60 border border-gray-700 rounded p-3">
                    <div class="text-gray-500 mb-1">crowdsourced_yara_results</div>
                    <div class="text-gray-200">{{ hashYaraCount }} 条</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="parsedResult">
              <p class="text-gray-300 mb-4">
                综合 <strong class="text-gray-200">cxn_cnn</strong> 与
                <strong class="text-gray-200">VirusTotal</strong> 多引擎结果。
              </p>
              <p v-if="parsedResult.cxn_models_note" class="text-xs text-gray-500 mb-4">
                {{ parsedResult.cxn_models_note }}
              </p>
              <div class="grid sm:grid-cols-2 gap-6">
                <div class="bg-gray-900/60 rounded-lg p-4">
                  <h3 class="text-sm font-semibold text-green-400 mb-3">综合结论</h3>
                  <p class="text-xl font-bold" :class="parsedResult.is_malware ? 'text-red-400' : 'text-green-400'">
                    {{ parsedResult.is_malware ? '恶意软件' : '安全文件' }}
                  </p>
                  <p class="text-sm text-gray-500 mt-2">
                    置信度 {{ (parsedResult.confidence * 100).toFixed(1) }}%
                  </p>
                </div>
                <div class="bg-gray-900/60 rounded-lg p-4">
                  <h3 class="text-sm font-semibold text-green-400 mb-3">cxn 模型得分</h3>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-400">cxn_cnn 家族置信度</span>
                      <span>{{ ((parsedResult.family_confidence ?? parsedResult.cnn_score ?? 0) * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="flex justify-between" v-if="parsedResult.cnn_detail?.predicted_label">
                      <span class="text-gray-400">预测家族类别</span>
                      <span>Class {{ parsedResult.cnn_detail.predicted_label }}</span>
                    </div>
                  </div>
                  <div
                    v-if="cnnClassProbabilityEntries.length"
                    class="mt-4 rounded border border-gray-700 overflow-hidden"
                  >
                    <div class="px-3 py-2 text-xs text-gray-400 bg-gray-950/70">
                      CNN 各类别概率（降序）
                    </div>
                    <div class="max-h-44 overflow-y-auto">
                      <table class="min-w-full text-xs">
                        <thead class="bg-gray-950/50">
                          <tr>
                            <th class="px-3 py-2 text-left text-gray-400">类别</th>
                            <th class="px-3 py-2 text-left text-gray-400">概率</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="entry in cnnClassProbabilityEntries"
                            :key="entry.label"
                            class="border-t border-gray-800"
                          >
                            <td class="px-3 py-2 text-gray-200">Class {{ entry.label }}</td>
                            <td class="px-3 py-2 text-gray-300">{{ (entry.probability * 100).toFixed(2) }}%</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div ref="barChartEl" class="mt-6 h-40 w-full"></div>
                </div>
              </div>

              <!-- VirusTotal -->
              <div
                v-if="parsedResult.virustotal?.configured && parsedResult.virustotal.status === 'ok'"
                class="mt-6 bg-gray-900/60 rounded-lg p-4 border border-gray-700"
              >
                <h3 class="text-sm font-semibold text-green-400 mb-3">VirusTotal 多引擎</h3>
                <div class="grid sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-gray-500">恶意 / 可疑引擎数</span>
                    <p class="text-lg font-mono text-gray-100">
                      {{ parsedResult.virustotal.stats?.malicious_votes ?? 0 }}
                      <span class="text-gray-500">/</span>
                      {{ parsedResult.virustotal.stats?.total_engines ?? '—' }}
                    </p>
                  </div>
                  <div v-if="parsedResult.virustotal.meaningful_name" class="text-gray-400 break-all">
                    VT 名称：{{ parsedResult.virustotal.meaningful_name }}
                  </div>
                </div>
                <a
                  v-if="parsedResult.virustotal.permalink"
                  :href="parsedResult.virustotal.permalink"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block mt-3 text-green-400 hover:text-green-300 text-sm"
                >
                  在 VirusTotal 网页查看 →
                </a>
              </div>
              <div
                v-else-if="parsedResult.virustotal && !parsedResult.virustotal.configured"
                class="mt-6 text-sm text-gray-500 bg-gray-900/40 rounded-lg p-4"
              >
                未配置 VIRUSTOTAL_API_KEY，已跳过 VirusTotal 云端检测。
              </div>
              <div
                v-else-if="parsedResult.virustotal?.status === 'error'"
                class="mt-6 text-sm text-red-400/90 bg-red-950/30 rounded-lg p-4"
              >
                VirusTotal：{{ parsedResult.virustotal.error || '请求失败' }}
              </div>
            </div>
            <div v-else-if="result.result" class="text-gray-300 text-sm">
              <p class="mb-2 text-gray-500">未解析为 JSON 模型结果，原始结果见「详细信息」。</p>
            </div>
            <div v-else class="text-gray-500 text-sm">
              暂无检测结果，请稍后刷新或查看「详细信息」。
            </div>
          </div>

          <!-- 详细信息 -->
          <div v-show="activePanel === 'detail'" class="space-y-4">
            <template v-if="resultKind === 'url' && urlEnvelope">
              <label class="block text-xs text-gray-500">URL 检测 JSON 明细</label>
              <pre
                class="bg-gray-900 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-[480px] overflow-y-auto"
              >{{ urlDetailJson }}</pre>
            </template>
            <template v-else-if="resultKind === 'hash' && hashEnvelope">
              <label class="block text-xs text-gray-500">哈希检测 JSON 明细</label>
              <pre
                class="bg-gray-900 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-[480px] overflow-y-auto"
              >{{ hashDetailJson }}</pre>
            </template>
            <template v-else>
            <label class="block text-xs text-gray-500">原始 JSON / 文本</label>
            <pre
              class="bg-gray-900 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-[480px] overflow-y-auto"
            >{{ detailJson }}</pre>
            </template>
          </div>

          <!-- 社区讨论 -->
          <div v-show="activePanel === 'community'" class="space-y-4">
            <p class="text-gray-400 text-sm">
              社区讨论功能即将开放，敬请期待。您可在此留下对样本判定的意见或参考链接（占位）。
            </p>
            <textarea
              rows="5"
              disabled
              class="w-full rounded-lg bg-gray-900 border border-gray-700 border-dashed px-3 py-2 text-sm text-gray-500 cursor-not-allowed resize-none"
              placeholder="讨论区暂未开放…"
            />
            <p class="text-xs text-gray-600">提示：上线后将支持用户评论与引用情报。</p>
          </div>
        </div>
      </template>

      <div v-else class="text-center py-16">
        <p class="text-gray-400">未找到检测结果</p>
        <router-link to="/" class="text-green-400 hover:text-green-300 mt-4 inline-block">
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../lib/api'
import * as echarts from 'echarts'

const RESULTS_PREVIEW_KEY = 'foxhunter_results_preview'

const route = useRoute()
const result = ref(null)
const loading = ref(true)
const parsedResult = ref(null)
const donutChartEl = ref(null)
const barChartEl = ref(null)
const activePanel = ref('result')

const tabs = [
  { key: 'result', label: '检测结果' },
  { key: 'detail', label: '详细信息' },
  { key: 'community', label: '社区讨论' }
]

/** file | url | hash — 用于圆环占位（默认 file） */
const resultKind = computed(() => {
  const t = (route.query.type || 'file').toString().toLowerCase()
  if (t === 'url' || t === 'hash') return t
  return 'file'
})

const kindLabel = computed(() => {
  const k = resultKind.value
  if (k === 'url') return 'URL 检测'
  if (k === 'hash') return '哈希查询'
  return '文件检测（样本）'
})

const subjectLabel = computed(() => {
  const k = resultKind.value
  if (k === 'url') return '检测 URL'
  if (k === 'hash') return '哈希值'
  return '文件名'
})

const voteCaption = computed(() => {
  if (resultKind.value === 'file') {
    const vt = parsedResult.value?.virustotal
    if (vt?.status === 'ok' && vt.stats?.total_engines) {
      return 'VirusTotal引擎投票'
    }
    return 'CNN 家族结果（VT 引擎未接入）'
  }
  if (resultKind.value === 'url') return 'URLhaus引擎投票'
  if (resultKind.value === 'hash') return 'VirusTotal引擎投票'
  return '引擎结果'
})

const voteStats = computed(() => {
  if (resultKind.value === 'url') {
    const mal = parsedResult.value?.is_malware ? 1 : 0
    return {
      malicious: mal,
      total: 1,
      label: '1/1'
    }
  }
  if (resultKind.value === 'hash') {
    const total = Number(hashTotalEngines.value ?? 0)
    if (total > 0) {
      const mal = Math.min(Math.max(Number(hashMalicious.value ?? 0), 0), total)
      return {
        malicious: mal,
        total,
        label: `${mal}/${total}`
      }
    }
    const fallbackMal = parsedResult.value?.is_malware ? 1 : 0
    return {
      malicious: fallbackMal,
      total: 1,
      label: '1/1'
    }
  }
  const vt = parsedResult.value?.virustotal
  if (vt?.status === 'ok' && vt.stats?.total_engines) {
    const mal = Number(vt.stats.malicious_votes ?? 0)
    const total = Math.max(Number(vt.stats.total_engines), 1)
    return {
      malicious: mal,
      total,
      label: `${mal}/${total}`
    }
  }
  return {
    malicious: 1,
    total: 10,
    label: '1/10'
  }
})

const verdictText = computed(() => {
  if (!result.value) return '—'
  if (result.value.status !== 'completed') {
    return result.value.status === 'failed' ? '检测失败' : '处理中'
  }
  if (parsedResult.value && typeof parsedResult.value.is_malware === 'boolean') {
    return parsedResult.value.is_malware ? '恶意' : '安全'
  }
  if (result.value.result) return '已返回（未解析）'
  return '暂无结果'
})

const verdictClass = computed(() => {
  if (!result.value || result.value.status !== 'completed') return 'text-gray-300'
  if (parsedResult.value && typeof parsedResult.value.is_malware === 'boolean') {
    return parsedResult.value.is_malware ? 'text-red-400' : 'text-green-400'
  }
  return 'text-gray-200'
})

const detailJson = computed(() => {
  if (!result.value) return ''
  const r = result.value.result
  if (r == null || r === '') return '（无）'
  if (typeof r === 'string') {
    try {
      return JSON.stringify(JSON.parse(r), null, 2)
    } catch {
      return r
    }
  }
  return JSON.stringify(r, null, 2)
})

const urlEnvelope = computed(() => {
  if (resultKind.value !== 'url' || !result.value?.result) return null
  try {
    const obj = typeof result.value.result === 'string' ? JSON.parse(result.value.result) : result.value.result
    return obj && typeof obj === 'object' ? obj : null
  } catch {
    return null
  }
})

const urlRaw = computed(() => {
  const env = urlEnvelope.value
  if (!env) return null
  const raw = env.raw_result ?? env
  return raw && typeof raw === 'object' ? raw : null
})

const urlDetailJson = computed(() => {
  if (!urlEnvelope.value) return '（无）'
  const payload = urlRaw.value || urlEnvelope.value
  return JSON.stringify(payload, null, 2)
})

const urlQueryStatus = computed(() => {
  const raw = urlRaw.value || {}
  return raw.query_status || raw.status || '—'
})

const urlStatus = computed(() => {
  const raw = urlRaw.value || {}
  const info = raw.url_info || {}
  return raw.url_status || info.url_status || raw.threat || '—'
})

const urlThreatLevel = computed(() => {
  const raw = urlRaw.value || {}
  const blacklisted = raw.blacklists || raw.blacklisted
  if (typeof blacklisted === 'string') return blacklisted
  if (Array.isArray(blacklisted)) return blacklisted.length ? '是' : '否'
  if (blacklisted && typeof blacklisted === 'object') return Object.keys(blacklisted).length ? '是' : '否'
  return '未知'
})

const urlTags = computed(() => {
  const raw = urlRaw.value || {}
  const tags = raw.tags || raw.tag || []
  if (Array.isArray(tags)) return tags.map((t) => String(t))
  if (typeof tags === 'string' && tags.trim()) return [tags.trim()]
  return []
})

const urlPayloads = computed(() => {
  const raw = urlRaw.value || {}
  return Array.isArray(raw.payloads) ? raw.payloads : []
})

const urlBlacklistEntries = computed(() => {
  const raw = urlRaw.value || {}
  const b = raw.blacklists
  if (!b || typeof b !== 'object' || Array.isArray(b)) return []
  return Object.entries(b).map(([name, value]) => ({ name, value }))
})

const hashEnvelope = computed(() => {
  if (resultKind.value !== 'hash' || !result.value?.result) return null
  try {
    const obj = typeof result.value.result === 'string' ? JSON.parse(result.value.result) : result.value.result
    return obj && typeof obj === 'object' ? obj : null
  } catch {
    return null
  }
})

const hashRaw = computed(() => {
  const env = hashEnvelope.value
  if (!env) return null
  const raw = env.raw_result ?? env
  return raw && typeof raw === 'object' ? raw : null
})

const hashData = computed(() => hashRaw.value?.data || null)
const hashAttr = computed(() => hashData.value?.attributes || {})
const hashNames = computed(() => {
  const names = hashAttr.value?.names
  return Array.isArray(names) ? names.map((n) => String(n)) : []
})
const hashElfInfo = computed(() => hashAttr.value?.elf_info || null)
const hashSectionCount = computed(() => {
  const list = hashElfInfo.value?.section_list
  return Array.isArray(list) ? list.length : 0
})
const hashSegmentCount = computed(() => {
  const list = hashElfInfo.value?.segment_list
  return Array.isArray(list) ? list.length : 0
})

const hashDetailJson = computed(() => {
  if (!hashEnvelope.value) return '（无）'
  const payload = hashRaw.value || hashEnvelope.value
  return JSON.stringify(payload, null, 2)
})

const hashStats = computed(() => hashRaw.value?.data?.attributes?.last_analysis_stats || {})
const hashMalicious = computed(() => {
  const s = hashStats.value
  return Number(s.malicious ?? 0) + Number(s.suspicious ?? 0)
})
const hashTotalEngines = computed(() => {
  const s = hashStats.value
  const vals = Object.values(s).map((v) => Number(v) || 0)
  return vals.length ? vals.reduce((a, b) => a + b, 0) : null
})
const hashLastAnalysisDate = computed(() => {
  const ts = hashRaw.value?.data?.attributes?.last_analysis_date
  if (!ts) return null
  try {
    return new Date(Number(ts) * 1000).toLocaleString('zh-CN')
  } catch {
    return null
  }
})
const hashTypeTag = computed(() => hashRaw.value?.data?.attributes?.type_tag || null)
const hashTags = computed(() => {
  const tags = hashRaw.value?.data?.attributes?.tags
  return Array.isArray(tags) ? tags.map((t) => String(t)) : []
})
const hashThreatLabel = computed(
  () => hashAttr.value?.popular_threat_classification?.suggested_threat_label || null
)
const hashEngineEntries = computed(() => {
  const obj = hashAttr.value?.last_analysis_results
  if (!obj || typeof obj !== 'object') return []
  return Object.entries(obj).map(([name, v]) => ({
    name,
    category: v?.category,
    result: v?.result,
    version: v?.engine_version
  }))
})
const hashAiCount = computed(() => {
  const arr = hashAttr.value?.crowdsourced_ai_results
  return Array.isArray(arr) ? arr.length : 0
})
const hashYaraCount = computed(() => {
  const arr = hashAttr.value?.crowdsourced_yara_results
  return Array.isArray(arr) ? arr.length : 0
})

const cnnClassProbabilityEntries = computed(() => {
  const raw = parsedResult.value?.cnn_detail?.class_probabilities
  if (!raw || typeof raw !== 'object') return []
  return Object.entries(raw)
    .map(([label, probability]) => ({
      label: String(label),
      probability: Number(probability) || 0
    }))
    .sort((a, b) => b.probability - a.probability)
})

function formatUnixTs(ts) {
  if (ts == null || ts === '') return null
  const n = Number(ts)
  if (!Number.isFinite(n) || n <= 0) return null
  return new Date(n * 1000).toLocaleString('zh-CN')
}

function engineCategoryClass(cat) {
  if (cat === 'malicious') return 'text-red-400'
  if (cat === 'suspicious') return 'text-yellow-400'
  if (cat === 'undetected') return 'text-gray-300'
  if (cat === 'harmless') return 'text-green-400'
  return 'text-gray-400'
}

function displayOrNull(v) {
  if (v == null) return 'NULL'
  if (typeof v === 'string' && v.trim() === '') return 'NULL'
  return String(v)
}

let donutChart = null
let barChart = null

function buildDonutOption() {
  const { malicious, total, label } = voteStats.value
  const safe = Math.max(0, total - malicious)
  return {
    series: [
      {
        type: 'pie',
        radius: ['52%', '72%'],
        avoidLabelOverlap: false,
        itemStyle: { borderColor: '#1f2937', borderWidth: 2 },
        label: { show: false },
        emphasis: { disabled: true },
        data: [
          { value: malicious, name: '恶意', itemStyle: { color: '#f87171' } },
          { value: safe, name: '未判定恶意', itemStyle: { color: '#4ade80' } }
        ]
      }
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '42%',
        style: {
          text: label,
          fill: '#f3f4f6',
          fontSize: 22,
          fontWeight: 'bold'
        }
      },
      {
        type: 'text',
        left: 'center',
        top: '54%',
        style: {
          text: '投票数',
          fill: '#9ca3af',
          fontSize: 12
        }
      }
    ],
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    }
  }
}

function renderDonut() {
  nextTick(() => {
    if (!donutChartEl.value || !result.value) return
    if (!donutChart) donutChart = echarts.init(donutChartEl.value)
    donutChart.setOption(buildDonutOption(), true)
  })
}

function renderBar() {
  if (!parsedResult.value) return
  nextTick(() => {
    if (!barChartEl.value || !parsedResult.value) return
    if (!barChart) barChart = echarts.init(barChartEl.value)
    const v = parsedResult.value
    barChart.setOption({
      grid: { left: 40, right: 16, top: 16, bottom: 24 },
      xAxis: { type: 'category', data: ['CNN'] },
      yAxis: { type: 'value', max: 1, axisLabel: { formatter: (v) => `${(v * 100).toFixed(0)}%` } },
      series: [
        {
          type: 'bar',
          data: [v.cnn_score ?? v.family_confidence ?? 0],
          itemStyle: { color: '#4ade80', borderRadius: [4, 4, 0, 0] }
        }
      ],
      tooltip: { formatter: '{b}: {c}' }
    })
  })
}

function disposeCharts() {
  donutChart?.dispose()
  donutChart = null
  barChart?.dispose()
  barChart = null
}

function onResize() {
  donutChart?.resize()
  barChart?.resize()
}

let pollTimer = null

function clearPoll() {
  if (pollTimer != null) {
    clearTimeout(pollTimer)
    pollTimer = null
  }
}

function loadFromPreview() {
  const raw = sessionStorage.getItem(RESULTS_PREVIEW_KEY)
  if (!raw) {
    result.value = null
    parsedResult.value = null
    return
  }
  try {
    const { type, data, at } = JSON.parse(raw)
    const created = at ? new Date(at).toISOString() : new Date().toISOString()
    if (type === 'url' && data) {
      result.value = {
        id: null,
        filename: data.url || '—',
        status: 'completed',
        result: JSON.stringify(data),
        created_at: created
      }
    } else if (type === 'hash' && data) {
      result.value = {
        id: null,
        filename: data.hash || data.file_hash || '—',
        status: 'completed',
        result: JSON.stringify(data),
        created_at: created
      }
    }
    if (result.value?.result) {
      try {
        const outer = JSON.parse(result.value.result)
        if (outer && typeof outer.is_malware === 'boolean') {
          parsedResult.value = outer
        } else {
          parsedResult.value = null
        }
      } catch {
        parsedResult.value = null
      }
    }
  } catch (e) {
    console.error(e)
    result.value = null
    parsedResult.value = null
  }
}

async function fetchSampleResult(id) {
  const response = await api.get(`/api/v1/result/${id}`)
  result.value = response.data
  if (response.data.result) {
    try {
      parsedResult.value =
        typeof response.data.result === 'string'
          ? JSON.parse(response.data.result)
          : response.data.result
    } catch {
      parsedResult.value = null
    }
  } else {
    parsedResult.value = null
  }
  return response.data.status
}

async function loadResult(id) {
  clearPoll()
  disposeCharts()
  loading.value = true
  result.value = null
  parsedResult.value = null

  if (id === 'preview') {
    try {
      loadFromPreview()
    } finally {
      loading.value = false
    }
    return
  }

  try {
    const status = await fetchSampleResult(id)
    loading.value = false
    if (status === 'pending' || status === 'processing') {
      const poll = async () => {
        try {
          const s = await fetchSampleResult(id)
          if (s === 'pending' || s === 'processing') {
            pollTimer = setTimeout(poll, 2000)
          }
        } catch (e) {
          console.error(e)
        }
      }
      pollTimer = setTimeout(poll, 2000)
    }
  } catch (e) {
    console.error('Failed to load result:', e)
    loading.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (id) loadResult(id)
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  clearPoll()
  window.removeEventListener('resize', onResize)
  disposeCharts()
})

watch(
  [result, voteStats, resultKind],
  () => {
    nextTick(() => renderDonut())
  },
  { deep: true }
)

watch(
  [parsedResult, activePanel],
  () => {
    if (activePanel.value !== 'result') return
    nextTick(() => renderBar())
  },
  { deep: true }
)

watch(activePanel, (panel) => {
  if (panel === 'result') {
    nextTick(() => {
      renderDonut()
      renderBar()
    })
  }
})

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusColor = (status) => {
  switch (status) {
    case 'completed':
      return 'text-green-400'
    case 'failed':
      return 'text-red-400'
    case 'processing':
      return 'text-yellow-400'
    default:
      return 'text-gray-400'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'completed':
      return '检测完成'
    case 'failed':
      return '检测失败'
    case 'processing':
      return '检测中'
    default:
      return '等待中'
  }
}
</script>

<style scoped>
</style>
