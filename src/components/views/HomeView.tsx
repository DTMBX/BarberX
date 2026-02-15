import { useKV } from '@github/spark/hooks'
import { BookOpen, BookmarkSimple, Clock as ClockIcon } from '@phosphor-icons/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { UserProfile, Bookmark } from '@/lib/types'
import { bibleBooks } from '@/lib/data'
import VerseOfTheDay from '@/components/VerseOfTheDay'

interface HomeViewProps {
  userProfile: UserProfile
  onNavigateToReader?: (bookId: string, chapter: number) => void
  onNavigateToMessages?: (friendId: string, verseRef?: any) => void
}

export default function HomeView({ userProfile, onNavigateToReader, onNavigateToMessages }: HomeViewProps) {
  const [bookmarks = []] = useKV<Bookmark[]>('bookmarks', [])
  const lastRead = userProfile?.lastReadPosition

  const lastReadBook = lastRead ? bibleBooks.find(b => b.id === lastRead.workId) : null

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h2 className="text-3xl font-bold mb-2 text-foreground" style={{ fontFamily: 'var(--font-heading)' }}>
          Welcome to the Geneva Bible
        </h2>
        <p className="text-muted-foreground text-lg">
          The Bible of the Protestant Reformation, now available for deep study and comparison
        </p>
      </div>

      <div className="mb-8">
        <VerseOfTheDay 
          userProfile={userProfile} 
          onNavigateToReader={onNavigateToReader}
          onNavigateToMessages={onNavigateToMessages}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <Card className="border-l-4 border-l-primary hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen size={24} weight="duotone" className="text-primary" />
                  Continue Reading
                </CardTitle>
                <CardDescription>Pick up where you left off</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {lastReadBook && lastRead ? (
              <div>
                <p className="text-xl font-semibold mb-2" style={{ fontFamily: 'var(--font-heading)' }}>
                  {lastReadBook.title} {lastRead.chapterNumber}:{lastRead.verseNumber}
                </p>
                <Badge variant="secondary" className="mb-4">
                  {userProfile?.preferences.defaultTranslation.toUpperCase()}
                </Badge>
                <Button className="w-full">
                  <BookOpen size={20} weight="duotone" className="mr-2" />
                  Continue Reading
                </Button>
              </div>
            ) : (
              <div>
                <p className="text-muted-foreground mb-4">
                  Start your journey through the Geneva Bible
                </p>
                <Button className="w-full">
                  <BookOpen size={20} weight="duotone" className="mr-2" />
                  Begin with Genesis
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-accent hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookmarkSimple size={24} weight="duotone" className="text-accent" />
              Recent Bookmarks
            </CardTitle>
            <CardDescription>Your saved passages</CardDescription>
          </CardHeader>
          <CardContent>
            {bookmarks.length > 0 ? (
              <div className="space-y-3">
                {bookmarks.slice(0, 3).map((bookmark) => {
                  const book = bibleBooks.find(b => b.id === bookmark.workId)
                  return (
                    <div
                      key={bookmark.id}
                      className="flex items-start justify-between p-3 rounded-md bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                    >
                      <div>
                        <p className="font-medium">
                          {book?.shortName} {bookmark.chapterNumber}:{bookmark.verseNumber}
                        </p>
                        {bookmark.label && (
                          <p className="text-sm text-muted-foreground">{bookmark.label}</p>
                        )}
                      </div>
                    </div>
                  )
                })}
                {bookmarks.length > 3 && (
                  <Button variant="ghost" size="sm" className="w-full">
                    View all {bookmarks.length} bookmarks
                  </Button>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-muted-foreground">
                <BookmarkSimple size={48} weight="duotone" className="mx-auto mb-2 opacity-50" />
                <p>No bookmarks yet</p>
                <p className="text-sm">Bookmark verses as you read</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="text-lg">Understanding Translations</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Learn why English Bibles differ and how to choose translations for different purposes
            </p>
            <Button variant="outline" className="w-full">
              Explore Translation Guide
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <ClockIcon size={20} weight="duotone" />
              Biblical Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Explore how the biblical library formed across history and traditions
            </p>
            <Button variant="outline" className="w-full">
              View Timeline
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer border-accent/50">
          <CardHeader>
            <CardTitle className="text-lg">The Geneva Difference</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Why the Geneva Bible shaped the Reformation and influenced the King James Version
            </p>
            <Button variant="outline" className="w-full">
              Learn More
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
